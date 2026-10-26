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
            "서버 클러스터링: 부하 분산": "인프라/DevOps",
            "React UI": "웹/프론트엔드",
        }
        for topic, expected in cases.items():
            with self.subTest(topic=topic):
                self.assertEqual(build.resolve_category(topic), expected)

    def test_english_keyword_not_matched_inside_word(self):
        self.assertNotEqual(build.resolve_category("UUID와 ULID"), "웹/프론트엔드")


class CheckStepsTest(unittest.TestCase):
    SVG = '<svg><g data-edge="e-react-server" data-from="react" data-to="server"></g></svg>'

    def test_code_over_mode_limit(self):
        code = "\n".join(f"line{i}" for i in range(16))
        steps = f"[{{ summary: '', code: `{code}`, nodes: [], edges: [] }}]"
        self.assertIn("1단계 코드 16줄 (구현 모드 상한 15줄)", build.check_steps(steps, self.SVG, "구현 모드"))

    def test_summary_with_many_english_terms(self):
        steps = "[{ summary: 'x5c 안의 OID를 DER로 풀고 retainUntilConsumed 확인', nodes: [], edges: [] }]"
        self.assertIn(
            "1단계 설명에 영문 용어 4개 (x5c, OID, DER, retainUntilConsumed)",
            build.check_steps(steps, self.SVG, "개념 모드"),
        )

    def test_lit_edge_with_dim_endpoint(self):
        steps = "[{ summary: '', nodes: ['server'], edges: ['e-react-server'] }]"
        self.assertEqual(
            build.check_steps(steps, self.SVG, "개념 모드"),
            ["1단계 화살표 e-react-server가 켜졌는데 react 노드가 꺼져 있음"],
        )


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
