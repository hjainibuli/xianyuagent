import os
import unittest
from unittest.mock import patch

from XianyuApis import RiskControlError, XianyuApis, _build_browser_headers


class FakeResponse:
    headers = {}

    @staticmethod
    def json():
        return {"ret": ["SUCCESS::调用成功"], "data": {"accessToken": "token"}}


class RiskResponse:
    headers = {}

    @staticmethod
    def json():
        return {
            "ret": [
                "FAIL_SYS_USER_VALIDATE",
                "RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试",
            ]
        }


class RequestProfileTests(unittest.TestCase):
    def test_headers_are_consistent_and_configurable(self):
        with patch.dict(
            os.environ,
            {
                "CHROME_MAJOR_VERSION": "150.0.7871.187",
                "BROWSER_ACCEPT_LANGUAGE": "zh-CN,zh;q=0.9",
            },
            clear=False,
        ):
            headers = _build_browser_headers()

        self.assertIn("Chrome/150.0.0.0", headers["user-agent"])
        self.assertEqual("zh-CN,zh;q=0.9", headers["accept-language"])
        self.assertFalse(any(name.startswith("sec-ch-") for name in headers))
        self.assertFalse(any(name.startswith("sec-fetch-") for name in headers))

    def test_token_timestamp_uses_millisecond_precision(self):
        api = XianyuApis()
        api.session.cookies.set("_m_h5_tk", "signing-token_9999999999999")
        captured = {}

        def fake_post(url, headers, params, data):
            captured.update(url=url, headers=headers, params=params, data=data)
            return FakeResponse()

        with patch.object(api.session, "post", side_effect=fake_post), patch(
            "XianyuApis.time.time", return_value=1234.5678
        ):
            result = api.get_token("stable-device-id")

        self.assertEqual("1234567", captured["params"]["t"])
        self.assertEqual(api.url, captured["url"])
        self.assertNotIn("spm_pre", captured["params"])
        self.assertNotIn("log_id", captured["params"])
        self.assertIn("accessToken", result["data"])

    def test_risk_control_stops_without_retrying_or_prompting(self):
        api = XianyuApis()
        api.session.cookies.set("_m_h5_tk", "signing-token_9999999999999")

        with patch.object(api.session, "post", return_value=RiskResponse()) as post:
            with self.assertRaises(RiskControlError):
                api.get_token("device-id")

        post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
