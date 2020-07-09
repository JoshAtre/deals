import unittest

from deals import redirect_link
from deals import remove_query_string
from deals import get_body


class MyTestCase(unittest.TestCase):
    def test_redirect_link(self):
        urls = [{"original": "http://instagram.com", "final": "https://www.instagram.com/"},
                {"original": "https://www.instagram.com/", "final": "https://www.instagram.com/"},
                {"original": "http://google.com", "final": "https://www.google.com/?gws_rd=ssl"}]
        for url in urls:
            self.assertEqual(url["final"], redirect_link(url["original"]))

    def test_remove_query_string(self):
        urls = [{"original": "http://click.em.oshkosh.com/?qs=82fbc0f55914cd1d41b5e30639dfea2185226e67bba66bc3c38db6e9ee1fbace6734f4459df7e2835d3f0478a7125a3beb78578a79962c00",
                 "final": "http://click.em.oshkosh.com/"},
                 {"original": "https://click.online.costco.com/t?r=2&c=149345&l=121&ctl=6A51D5:1E26392660032F926DCE69357AC3E5384BAD797B5EF9BCDE",
                  "final": "https://click.online.costco.com/t"},
                 {"original": "https://click.emailinfo2.bestbuy.com/?qs=6ece0d116981f18a9ef0cbe100e493fcaf9145eb637acb9fe9622bb299b133ea207fe04129e48f5695fd6f788fac91f94a6b81db2e7a198f",
                  "final": "https://click.emailinfo2.bestbuy.com/"}]
        for url in urls:
            self.assertEqual(url["final"], remove_query_string(url["original"]))

    def test_get_body(self):
        url = "https://www.instagram.com"
        body = get_body(url)
        self.assertTrue(len(body) > 0)

        url = "https://www.instagram.com/ojoij4t5joijfg.com"
        try:
            body = get_body(url)
            self.assertTrue(False)
        except Exception as e:
            pass


if __name__ == '__main__':
    unittest.main()
