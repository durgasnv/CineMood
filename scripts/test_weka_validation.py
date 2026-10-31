"""Optional real-WEKA regression tests: set WEKA_JAR to enable these checks."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import prepare_data

JAR = os.environ.get("WEKA_JAR")
JAVA_SOURCE = Path(__file__).with_name("ValidateData.java").resolve()


@unittest.skipUnless(JAR and shutil.which("java"), "Set WEKA_JAR and install Java 11+ to check WEKA")
class WekaValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.target = self.root / "data/processed"
        self.target.mkdir(parents=True)
        for language in ("en", "hi"):
            records = [{"id": str(i), "split": "test", "text": f"don't यह फ़िल्म नहीं अच्छी {i}",
                        "label": label} for label in ("negative", "positive") for i in range(10)]
            with patch.object(prepare_data, "ROOT", self.root):
                prepare_data.write_outputs(language, records)

    def validate(self):
        return subprocess.run(["java", "-Dfile.encoding=UTF-8", "-cp", str(Path(JAR).resolve()), str(JAVA_SOURCE)],
                              cwd=self.root, text=True, capture_output=True, timeout=60)

    def test_real_exports_parse_and_preserve_apostrophes_and_unicode(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("hi: 20 rows; negative=10, positive=10", result.stdout)

    def test_empty_or_invalid_schema_is_rejected(self):
        path = self.target / "en_reviews.arff"
        good = path.read_text(encoding="utf-8")
        cases = {
            "empty": good.split("@data")[0] + "@data\n",
            "text_name": good.replace("@attribute review", "@attribute unrelated"),
            "class_name": good.replace("@attribute sentiment", "@attribute unrelated"),
            "class_order": good.replace("{negative,positive}", "{positive,negative}"),
            "class_values": good.replace("{negative,positive}", "{wrong,labels}"),
        }
        for name, invalid in cases.items():
            with self.subTest(name=name):
                path.write_text(invalid, encoding="utf-8")
                result = self.validate()
                self.assertNotEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
