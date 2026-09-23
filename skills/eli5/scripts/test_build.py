import unittest

import build


class ResolveCategoryTest(unittest.TestCase):
    def test_known_topics(self):
        cases = {
            "광합성": "자연과학",
            "블루투스 페어링": "네트워크/통신",
            "인플레이션": "경제/금융",
            "컴퓨터 비전 OCR": "인공지능/머신러닝",
            "데이터베이스 인덱스": "데이터베이스",
            "JWT 인증": "보안",
        }
        for topic, expected in cases.items():
            with self.subTest(topic=topic):
                self.assertEqual(build.resolve_category(topic), expected)


class CapTallSvgTest(unittest.TestCase):
    def test_tall_diagram_gets_max_width(self):
        self.assertEqual(
            build.cap_tall_svg('<svg viewBox="0 0 800 600"'),
            '<svg viewBox="0 0 800 600" style="max-width:560px;margin:0 auto"',
        )

    def test_flat_diagram_untouched(self):
        self.assertEqual(build.cap_tall_svg('<svg viewBox="0 0 940 250"'), '<svg viewBox="0 0 940 250"')


if __name__ == "__main__":
    unittest.main()
