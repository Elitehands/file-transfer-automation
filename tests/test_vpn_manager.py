def setUp(self):
    """Set up test environment before each test"""
    self.vpn_name = "bbuk vpn"
    self.vpn_manager = VPNManager(self.vpn_name)
    self.vpn_manager._test_hook = True  # Add this special test hook property