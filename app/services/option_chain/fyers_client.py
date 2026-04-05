import base64, time, asyncio
from functools import partial
import pyotp, requests
from urllib.parse import urlparse, parse_qs
from fyers_apiv3 import fyersModel

from app.core.config import settings
from app.utils.logger import logger

TOKEN_MAX_AGE_SECONDS = 20 * 3600  # re-login after 20 hours

class FyersClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._session = None
            cls._instance._login_time = None
        return cls._instance

    def _is_token_expired(self) -> bool:
        if self._login_time is None:
            return True
        return (time.time() - self._login_time) > TOKEN_MAX_AGE_SECONDS

    def get_session(self):
        if self._session is None or self._is_token_expired():
            logger.info("Fyers session missing or expired, logging in...")
            self._session = self._login()
            self._login_time = time.time() if self._session else None
        return self._session

    async def get_session_async(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_session)

    def invalidate(self):
        self._session = None
        self._login_time = None

    def _get_encoded(self, value: str) -> str:
        return base64.b64encode(value.encode("ascii")).decode("ascii")

    def _login(self):
        try:
            fy_id        = settings.FYERS_ID
            client_id    = settings.FYERS_CLIENT_ID
            secret_key   = settings.FYERS_SECRET_KEY
            redirect_uri = settings.FYERS_REDIRECT_URI
            totp_secret  = settings.FYERS_TOTP_SECRET
            pin          = settings.FYERS_PIN

            # Step 1 — Send OTP
            res = requests.post(
                "https://api-t2.fyers.in/vagator/v2/send_login_otp_v2",
                json={"fy_id": self._get_encoded(fy_id), "app_id": "2"}
            ).json()
            if res.get("s") != "ok":
                logger.error(f"OTP send failed: {res}")
                return None
            request_key = res["request_key"]

            # Step 2 — Verify TOTP
            if time.localtime().tm_sec % 30 > 27:
                time.sleep(5)
            totp = pyotp.TOTP(totp_secret).now()
            res = requests.post(
                "https://api-t2.fyers.in/vagator/v2/verify_otp",
                json={"request_key": request_key, "otp": totp}
            ).json()
            if res.get("s") != "ok":
                logger.error(f"OTP verify failed: {res}")
                return None
            request_key = res["request_key"]

            # Step 3 — Verify PIN
            ses = requests.Session()
            res = ses.post(
                "https://api-t2.fyers.in/vagator/v2/verify_pin_v2",
                json={"request_key": request_key, "identity_type": "pin",
                      "identifier": self._get_encoded(pin)}
            ).json()
            if res.get("s") != "ok":
                logger.error(f"PIN verify failed: {res}")
                return None
            ses.headers.update({"authorization": f"Bearer {res['data']['access_token']}"})

            # Step 4 — Get auth code
            res = ses.post(
                "https://api-t1.fyers.in/api/v3/token",
                json={"fyers_id": fy_id, "app_id": client_id[:-4],
                      "redirect_uri": redirect_uri, "appType": "100",
                      "response_type": "code", "create_cookie": True}
            ).json()
            if res.get("s") != "ok":
                logger.error(f"Auth code failed: {res}")
                return None
            auth_code = parse_qs(urlparse(res["Url"]).query).get("auth_code", [None])[0]

            # Step 5 — Exchange for access token
            sess = fyersModel.SessionModel(
                client_id=client_id, secret_key=secret_key,
                redirect_uri=redirect_uri, response_type="code",
                grant_type="authorization_code"
            )
            sess.set_token(auth_code)
            token_resp = sess.generate_token()
            if not token_resp or not token_resp.get("access_token"):
                logger.error(f"Token exchange failed: {token_resp}")
                return None

            fyers_obj = fyersModel.FyersModel(
                client_id=client_id,
                token=token_resp["access_token"],
                is_async=False,
                log_path=""
            )
            logger.info("Fyers login successful")
            return fyers_obj
        except Exception as e:
            logger.error(f"Fyers login exception: {e}")
            return None

fyers_client = FyersClient()