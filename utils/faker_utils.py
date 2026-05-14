"""假数据生成工具"""

from faker import Faker


class FakerTool:
    """基于 Faker 的通用假数据生成工具类"""

    def __init__(self, locale: str = "zh_CN"):
        self.faker = Faker(locale)

    # ---------- 基础信息 ----------
    def name(self) -> str:
        return self.faker.name()

    def phone(self) -> str:
        return self.faker.phone_number()

    def email(self) -> str:
        return self.faker.email()

    def address(self) -> str:
        return self.faker.address()

    def company(self) -> str:
        return self.faker.company()

    def id_card(self) -> str:
        return self.faker.ssn()

    # ---------- 数值 ----------
    def int(self, min_value: int = 0, max_value: int = 100) -> int:
        return self.faker.random_int(min=min_value, max=max_value)

    def float_num(self, min_value: float = 0, max_value: float = 100, precision: int = 2) -> float:
        return round(self.faker.pyfloat(min_value=min_value, max_value=max_value, positive=True), precision)

    # ---------- 文本 ----------
    def text(self, max_nb_chars: int = 20) -> str:
        return self.faker.text(max_nb_chars=max_nb_chars).replace("\n", "")

    def sentence(self) -> str:
        return self.faker.sentence()

    # ---------- 日期时间 ----------
    def date(self, pattern: str = "%Y-%m-%d") -> str:
        return self.faker.date(pattern=pattern)

    def datetime(self, pattern: str = "%Y-%m-%d %H:%M:%S") -> str:
        return self.faker.date_time().strftime(pattern)

    # ---------- 业务专用 ----------
    def strategy_name(self, prefix: str = "策略") -> str:
        """生成随机策略名称"""
        suffix = self.faker.word() + "_" + self.faker.date(pattern="%Y%m%d")
        return f"{prefix}_{suffix}"

    def stock_code(self) -> str:
        """生成随机 A 股代码（6 位数字）"""
        prefixes = ["600", "601", "603", "000", "002", "300", "688"]
        prefix = self.faker.random_element(elements=prefixes)
        return prefix + str(self.faker.random_int(min=0, max=999)).zfill(3)

    def stock_name(self) -> str:
        """生成随机股票名称"""
        return self.faker.word() + "股份"

    def strategy_description(self, max_sentences: int = 3) -> str:
        """生成随机策略描述文本"""
        sentences = [self.faker.sentence() for _ in range(self.faker.random_int(min=1, max=max_sentences))]
        return " ".join(sentences)


# 全局单例
faker_tool = FakerTool()
