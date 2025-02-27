from imswitch.imcommon.model import VFileItem
from imswitch.imcontrol.model import (
    #DetectorsManager, LasersManager, MultiManager, NidaqManager, PulseStreamerManager, PositionersManager,
    DetectorsManager, LasersManager, MultiManager, NidaqManager, PositionersManager,
    RecordingManager, RS232sManager, ScanManager, SLMManager
)


class MasterController:
    """
    This class will handle the communication between software and hardware,
    using the managers for each hardware set.
    """

    def __init__(self, setupInfo, commChannel, moduleCommChannel):
        self.__setupInfo = setupInfo
        self.__commChannel = commChannel
        self.__moduleCommChannel = moduleCommChannel

        # Init managers
        self.nidaqManager = NidaqManager(self.__setupInfo)
        #self.pulseStreamerManager = PulseStreamerManager(self.__setupInfo)
        self.rs232sManager = RS232sManager(self.__setupInfo.rs232devices)

        lowLevelManagers = {
            'nidaqManager': self.nidaqManager,
            #'pulseStreamerManager' : self.pulseStreamerManager,
            'rs232sManager': self.rs232sManager
        }

        self.detectorsManager = DetectorsManager(self.__setupInfo.detectors, updatePeriod=100,
                                                 **lowLevelManagers)
        self.lasersManager = LasersManager(self.__setupInfo.lasers,
                                           **lowLevelManagers)
        self.positionersManager = PositionersManager(self.__setupInfo.positioners,
                                                     **lowLevelManagers)

        self.scanManager = ScanManager(self.__setupInfo)
        self.recordingManager = RecordingManager(self.detectorsManager)
        self.slmManager = SLMManager(self.__setupInfo.slm)

        # Connect signals
        cc = self.__commChannel

        self.detectorsManager.sigAcquisitionStarted.connect(cc.sigAcquisitionStarted)
        self.detectorsManager.sigAcquisitionStopped.connect(cc.sigAcquisitionStopped)
        self.detectorsManager.sigDetectorSwitched.connect(cc.sigDetectorSwitched)
        self.detectorsManager.sigImageUpdated.connect(cc.sigUpdateImage)

        self.recordingManager.sigRecordingStarted.connect(cc.sigRecordingStarted)
        self.recordingManager.sigRecordingEnded.connect(cc.sigRecordingEnded)
        self.recordingManager.sigRecordingFrameNumUpdated.connect(cc.sigUpdateRecFrameNum)
        self.recordingManager.sigRecordingTimeUpdated.connect(cc.sigUpdateRecTime)
        self.recordingManager.sigMemorySnapAvailable.connect(cc.sigMemorySnapAvailable)
        self.recordingManager.sigMemoryRecordingAvailable.connect(self.memoryRecordingAvailable)

        self.slmManager.sigSLMMaskUpdated.connect(cc.sigSLMMaskUpdated)

    def memoryRecordingAvailable(self, name, file, filePath, savedToDisk):
        self.__moduleCommChannel.memoryRecordings[name] = VFileItem(
            data=file, filePath=filePath, savedToDisk=savedToDisk
        )

    def closeEvent(self):
        self.recordingManager.endRecording(emitSignal=False, wait=True)

        for attrName in dir(self):
            attr = getattr(self, attrName)
            if isinstance(attr, MultiManager):
                attr.finalize()


# Copyright (C) 2020-2021 ImSwitch developers
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
