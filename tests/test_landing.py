from pathlib import Path
from html.parser import HTMLParser
import struct
import unittest

ROOT=Path(__file__).resolve().parents[1]
CHECKOUT='https://pay.kiwify.com.br/8k9qMAH'

class Parse(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags=[]
        self.attributes=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
        self.attributes.append((tag,dict(attrs)))

class LandingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'index.html').read_text(encoding='utf-8')
        cls.parser=Parse()
        cls.parser.feed(cls.html)
    def test_single_h1_and_language(self):
        self.assertGreater(self.html.count('\n'),80)
        self.assertEqual(self.parser.tags.count('h1'),1)
        self.assertIn('<html lang="pt-BR">',self.html)
    def test_live_purchase_ctas(self):
        links=[a.get('href') for tag,a in self.parser.attributes if tag=='a']
        self.assertEqual(links.count(CHECKOUT),2)
        self.assertNotIn('será ativado',self.html)
    def test_real_product_images(self):
        images=[a for tag,a in self.parser.attributes if tag=='img']
        self.assertEqual(len(images),2)
        for img in images:
            self.assertTrue(img.get('alt'))
            self.assertEqual(img.get('loading'),'lazy')
            data=(ROOT/img['src']).read_bytes()
            self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II',data[16:24]),(1920,922))
    def test_offer_not_misleading(self):
        for phrase in ('R$29,90','pagamento único','dados de demonstração',
                       'O envio é manual','navegador deste dispositivo'):
            self.assertIn(phrase.lower(),self.html.lower())
    def test_encoding_repaired(self):
        for marker in ('Ã©','Ã£','Ã§','â€”','â€œ','â€'):
            self.assertNotIn(marker,self.html)
    def test_faq_complete(self):
        self.assertEqual(self.parser.tags.count('details'),4)
        self.assertEqual(self.parser.tags.count('summary'),4)

if __name__=='__main__':
    unittest.main(verbosity=2)
