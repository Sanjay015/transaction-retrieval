from unittest import TestCase, mock


class TestUtils(TestCase):
    def setUp(self) -> None:
        # patch `utils.utils.transaction_files`
        self.transaction_files_patch = mock.patch("utils.utils.transaction_files")
        self.mock_files_patcher = self.transaction_files_patch.start()
        self.mock_files_patcher.return_value = []

    def tearDown(self) -> None:
        self.mock_files_patcher.stop()

    def test_check(self):
        self.assertEqual(1, 1)
