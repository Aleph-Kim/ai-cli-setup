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
    def test_code_over_mode_limit(self):
        code = "\n".join(f"line{i}" for i in range(16))
        steps = f"[{{ summary: '', code: `{code}`, nodes: [], edges: [] }}]"
        self.assertIn("1단계 코드 16줄 (구현 모드 상한 15줄)", build.check_steps(steps, "구현 모드"))

    def test_mixed_mode_uses_concept_limit_only_in_first_phase(self):
        code = "\n".join(f"line{i}" for i in range(11))
        steps = (
            f"[{{ phase: '구조 이해', summary: '', code: `{code}` }},"
            f" {{ phase: '구현', summary: '', code: `{code}` }}]"
        )
        self.assertEqual(build.check_steps(steps, "혼합 모드"), ["1단계 코드 11줄 (개념 모드 상한 10줄)"])

    def test_summary_with_many_english_terms(self):
        steps = "[{ summary: 'x5c 안의 OID를 DER로 풀고 retainUntilConsumed 확인', nodes: [], edges: [] }]"
        self.assertIn(
            "1단계 설명에 영문 용어 4개 (x5c, OID, DER, retainUntilConsumed)",
            build.check_steps(steps, "개념 모드"),
        )


class CapTallSvgTest(unittest.TestCase):
    def test_tall_diagram_gets_max_width(self):
        self.assertEqual(
            build.cap_tall_svg('<svg viewBox="0 0 800 600"'),
            '<svg viewBox="0 0 800 600" style="max-width:560px;margin:0 auto"',
        )

    def test_small_text_widens_cap(self):
        self.assertEqual(
            build.cap_tall_svg('<svg viewBox="0 0 800 600"', 10),
            '<svg viewBox="0 0 800 600" style="max-width:960px;margin:0 auto"',
        )

    def test_large_text_keeps_height_cap(self):
        self.assertEqual(
            build.cap_tall_svg('<svg viewBox="0 0 800 600"', 24),
            '<svg viewBox="0 0 800 600" style="max-width:560px;margin:0 auto"',
        )

    def test_flat_diagram_untouched(self):
        self.assertEqual(build.cap_tall_svg('<svg viewBox="0 0 940 250"'), '<svg viewBox="0 0 940 250"')


SVG = """
<g data-edge="a-b" data-from="a" data-to="b"><path d="M0,0"/></g>
<g data-edge="a-c" data-from="a" data-to="c"><path d="M0,0"/></g>
<g data-node="a"></g><g data-node="b"></g><g data-node="c"></g>
<g data-node="box"></g><g data-node="cell" data-parent="box"></g>
"""


class CheckHighlightTest(unittest.TestCase):
    def check(self, steps):
        return build.check_highlight(SVG, steps)

    def test_consistent_steps_pass(self):
        errors, _ = self.check("[{nodes: ['a', 'b'], edges: ['a-b']}, {nodes: ['box', 'cell'], edges: []}]")
        self.assertEqual(errors, [])

    def test_lit_edge_with_dim_end_fails(self):
        errors, _ = self.check("[{nodes: ['a'], edges: ['a-b']}]")
        self.assertEqual(errors, ["1단계: 화살표 a-b 는 밝은데 끝 노드 b 는 흐림"])

    def test_lit_child_with_dim_parent_fails(self):
        errors, _ = self.check("[{nodes: ['cell'], edges: []}]")
        self.assertEqual(errors, ["1단계: 노드 cell 는 밝은데 부모 box 는 흐림"])

    def test_parent_without_children_warns(self):
        errors, warnings = self.check("[{nodes: ['box'], edges: []}]")
        self.assertEqual(errors, [])
        self.assertIn("1단계: box 는 밝은데 안의 노드 cell 가 모두 흐림", warnings)

    def test_bundled_edge_fails(self):
        svg = '<g data-edge="x" data-from="a" data-to="b"><path/><path/></g><g data-node="a"></g><g data-node="b"></g>'
        errors, _ = build.check_highlight(svg, "[{nodes: [], edges: []}]")
        self.assertEqual(errors, ["화살표 x: 선이 2개 이상. 끝점마다 data-edge 를 나눌 것"])

    def test_edge_without_endpoints_fails(self):
        errors, _ = build.check_highlight('<g data-edge="x"><path/></g>', "[{nodes: [], edges: []}]")
        self.assertEqual(errors, ["화살표 x: data-from / data-to 가 없음"])

    def test_all_lit_step_skips_endpoint_check(self):
        errors, _ = self.check("[{nodes: [], edges: []}]")
        self.assertEqual(errors, [])


class TagColorPairsTest(unittest.TestCase):
    def test_keeps_order_and_lowercases_keywords(self):
        self.assertEqual(
            build.tag_color_pairs('{"RabbitMQ": "#FF6600", "kafka": "#231F20"}'),
            '[["rabbitmq", "#FF6600"], ["kafka", "#231F20"]]',
        )

    def test_rejects_non_hex_color(self):
        with self.assertRaises(SystemExit):
            build.tag_color_pairs('{"kafka": "black"}')


if __name__ == "__main__":
    unittest.main()
