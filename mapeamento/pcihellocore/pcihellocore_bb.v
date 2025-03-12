
module pcihellocore (
	fan_control_external_connection_export,
	green_leds_external_connection_export,
	hex_display2_external_connection_export,
	hex_display3_external_connection_export,
	hex_display_external_connection_export,
	pcie_hard_ip_0_pcie_rstn_export,
	pcie_hard_ip_0_powerdown_pll_powerdown,
	pcie_hard_ip_0_powerdown_gxb_powerdown,
	pcie_hard_ip_0_refclk_export,
	pcie_hard_ip_0_rx_in_rx_datain_0,
	pcie_hard_ip_0_tx_out_tx_dataout_0,
	push_buttons_external_connection_export,
	red_leds_external_connection_export,
	switches_external_connection_export);	

	output	[31:0]	fan_control_external_connection_export;
	output	[31:0]	green_leds_external_connection_export;
	output	[31:0]	hex_display2_external_connection_export;
	output	[31:0]	hex_display3_external_connection_export;
	output	[31:0]	hex_display_external_connection_export;
	input		pcie_hard_ip_0_pcie_rstn_export;
	input		pcie_hard_ip_0_powerdown_pll_powerdown;
	input		pcie_hard_ip_0_powerdown_gxb_powerdown;
	input		pcie_hard_ip_0_refclk_export;
	input		pcie_hard_ip_0_rx_in_rx_datain_0;
	output		pcie_hard_ip_0_tx_out_tx_dataout_0;
	input	[31:0]	push_buttons_external_connection_export;
	output	[31:0]	red_leds_external_connection_export;
	input	[31:0]	switches_external_connection_export;
endmodule
