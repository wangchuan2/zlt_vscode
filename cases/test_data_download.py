"""测试用例：数据下载"""

from cases.base_test_case import BaseTestCase
from core.logger import get_logger
from pages.login_page import LoginPage
from pages.data_download_page import DataDownloadPage

logger = get_logger("case")


class TestDataDownload(BaseTestCase):
    """数据下载测试用例"""

    async def zztest_download(self) -> bool:
        """执行完整测试流程：登录 + 数据下载"""
        self._start_test(
            name="数据下载流程测试",
            description="智量通 VS Code 插件：登录 + 数据下载完整流程",
            labels={"feature": "数据下载", "severity": "critical"},
        )
        try:
            playwright, browser, page = await self._setup()

            login_page = LoginPage(page)
            if not await login_page.ensure_login():
                raise AssertionError("登录失败或无法确认登录状态")

            download_page = DataDownloadPage(page)
            if not await download_page.download_flow():
                raise AssertionError("数据下载流程失败")

            self._set_passed()
            return True

        except Exception as e:
            self._set_failed(str(e))
            return False
        finally:
            await self._teardown()


async def main():
    case = TestDataDownload()
    return await case.zztest_download()


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(main())
    exit(0 if result else 1)
