#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: PlutoOFDM
# Author: Jay
# Description: PlutoOFDM
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import numpy as np

from gnuradio import qtgui

class PlutoOFDM(gr.top_block, Qt.QWidget):

    def __init__(self, uri='ip:192.168.2.1'):
        gr.top_block.__init__(self, "PlutoOFDM")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("PlutoOFDM")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "PlutoOFDM")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Parameters
        ##################################################
        self.uri = uri

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 30720000
        self.ncarrier = ncarrier = 32
        self.fft_len = fft_len = 128
        self.cp_len = cp_len = 16

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            firdes.WIN_HAMMING, #wintype
            0, #fc
            samp_rate, #bw
            'Tx', #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win)
        self.fft_vxx_0 = fft.fft_vcc(128, False, window.blackmanharris(128), True, 1)
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + int(fft_len/8), 0, "packet_len")
        self.digital_ofdm_carrier_allocator_cvc_0 = digital.ofdm_carrier_allocator_cvc( fft_len, [list(range(-16,0)) + list(range(1, 17))], [[-(ncarrier+1),(ncarrier+1)]], [[1,1]] , (), "packet_len", True)
        self.digital_glfsr_source_x_0 = digital.glfsr_source_b(16, True, 0, 1)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc([-1-1j,-1+1j,1-1j,1+1j], 1)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, ncarrier, "packet_len")
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(1, 2, "", False, gr.GR_LSB_FIRST)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.digital_ofdm_carrier_allocator_cvc_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.digital_glfsr_source_x_0, 0), (self.blocks_repack_bits_bb_0, 0))
        self.connect((self.digital_ofdm_carrier_allocator_cvc_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "PlutoOFDM")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_uri(self):
        return self.uri

    def set_uri(self, uri):
        self.uri = uri

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_ncarrier(self):
        return self.ncarrier

    def set_ncarrier(self, ncarrier):
        self.ncarrier = ncarrier
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.ncarrier)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.ncarrier)

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len




def argument_parser():
    description = 'PlutoOFDM'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--uri", dest="uri", type=str, default='ip:192.168.2.1',
        help="Set URI [default=%(default)r]")
    return parser


def main(top_block_cls=PlutoOFDM, options=None):
    if options is None:
        options = argument_parser().parse_args()

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(uri=options.uri)

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
