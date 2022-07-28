UNIT_LENGTH = 170
DANGER_ZONE_DIAG = 600
# DETECTION_MODEL_PATH = 'models/imgs2126-11May-imgsize1024-yolov5l-ep80-valCOCO-0.49.pth'
DETECTION_MODEL_PATH = 'models/imgsize1280-yolor-mAP-0.603.pt'
DETECTION_CONF_THRESHOLD = 0.3
DETECTION_BATCH_SIZE = 16
REPORT_PAD = 140
OUTPUT_RES_RATIO = 1
USE_IV_MODEL = True
USE_YOLOR_MODEL = True
YOLOR_CLASS_NAMES = 'yolor/data/custom.names'
YOLOR_CONFIG = 'yolor/cfg/yolor_p6_custom.cfg'
YOLOR_IMG_SIZE = 1280
YOLOR_IOU_THRESHOLD = 0.5

MAX_DISTANCE_FOR_FORKLIFT = 1100
MAX_DISTANCE_FOR_SUSPENDED_LEAN_OBJECT = 1100
MAX_DISTANCE_FOR_CHAIN = 1100
MAX_DISTANCE_FOR_PEOPLE = 1100
MAX_DISTANCE_FOR_HUMAN_CARRIER = 1100

HUMAN_HEIGHT_COEFFICIENT = 90.98076923076923
FORKLIFT_HEIGHT_COEFFICIENT = 152.5385475180557
HUMAN_CARRIER_HEIGHT_COEFFICIENT = 132.57671290458177

REFERENCE_AREA_DICT = {
    '0.avi': [(24, 1364), (2525, 1321), (1587, 1005), (661, 958)],
    '1.avi': [(32, 1406), (2490, 1227), (1819, 177), (211, 384)],
    '2.avi': [(553, 1415), (2427, 1417), (1927, 769), (908, 775)],
    '3.avi': [(908, 1432), (1953, 1432), (1913, 851), (1025, 1093)],
    '4.avi': [(162, 1391), (2276, 1415), (1874, 590), (638, 566)], 
    '5.avi': [(9, 1066), (1911, 1050), (814, 707), (134, 680)],
    '6.avi': [(17, 1048), (1429, 984), (576, 652), (60, 623)],
    '7.avi': [(1310, 1057), (1898, 541), (1013, 374), (605, 542)],
    '8.avi': [(15, 538), (1802, 1067), (1642, 534), (1069, 471)],
    '9.avi': [(24, 1046), (1902, 885), (868, 719), (208, 691)],
    '10.avi': [(11, 1319), (2012, 1931), (1893, 1496), (474, 1139)],
    '11.avi': [(15, 1894), (2498, 1899), (2190, 1614), (311, 1689)],
    '12.avi': [(663, 1634), (2021, 1389), (1474, 789), (673, 844)],
    '13.avi': [(682, 1619), (2456, 1229), (1679, 677), (686, 757)],
    '14.avi': [(13, 1191), (2533, 1199), (2388, 396), (132, 405)],
    '15.avi': [(18, 1191), (2318, 1153), (2123, 399), (98, 422)],
    '16.avi': [(256, 610), (69, 1419), (2544, 1410), (2420, 620)],
    '17.avi': [(256, 610), (69, 1419), (2544, 1410), (2420, 620)],
    '18.avi': [(742, 1425), (2125, 1425), (2270, 1290), (1571, 1097)],
    '19.avi': [(742, 1425), (2125, 1425), (2270, 1290), (1571, 1097)],
    '20.avi': [(742, 1425), (2125, 1425), (2270, 1290), (1571, 1097)],
    '21.avi': [(496, 1919), (1135, 1917), (1345, 764), (785, 1112)],
    '22.avi': [(19, 1430), (2195, 968), (1576, 486), (30, 536)],
    '23.avi': [(19, 1430), (2195, 968), (1576, 486), (30, 536)],
    '24.avi': [(19, 1430), (2195, 968), (1576, 486), (30, 536)],
    '25.avi': [(306, 1426), (2456, 1406), (2193, 1039), (613, 1076)],
    '26.avi': [(230, 1420), (1793, 1429), (1598, 596), (532, 949)],
    '27.avi': [(334, 1429), (2064, 1039), (1603, 836), (251, 1014)],
    '28.avi': [(334, 1429), (2064, 1039), (1603, 836), (251, 1014)],
    '29.avi': [(334, 1429), (2064, 1039), (1603, 836), (251, 1014)],
    '30.avi': [(334, 1429), (2064, 1039), (1603, 836), (251, 1014)],
    '31.avi': [(334, 1429), (2064, 1039), (1603, 836), (251, 1014)]
}
EDGE_AREA_DICT= {
    '0.avi':[(1587, 1005), (661, 958)],
    '1.avi':[(32, 1406), (2490, 1227)],
    '2.avi':[(553, 1415), (2427, 1417)],
    '3.avi':[(1953, 1432), (1913, 851)],
    '4.avi': [(162, 1391), (2276, 1415)],
    '5.avi': [(1911, 1050), (814, 707)],
    '6.avi': [(1429, 984), (576, 652)],
    '7.avi': [(1310, 1057), (1898, 541)],
    '8.avi': [(15, 538), (1069, 471)],
    '9.avi': [(1902, 885), (868, 719)],
    '10.avi': [(11, 1319), (2012, 1931)],
    '11.avi': [(15, 1894), (2498, 1899)],
    '12.avi': [(663, 1634), (2021, 1389)],
    '13.avi': [(682, 1619), (2456, 1229)],
    '14.avi': [(13, 1191), (2533, 1199)],
    '15.avi': [(18, 1191), (2318, 1153)],
    '16.avi': [(2544, 1410), (2420, 620)],
    '17.avi': [(2544, 1410), (2420, 620)],
    '18.avi': [(2125, 1425), (2270, 1290)],
    '19.avi': [(2125, 1425), (2270, 1290)],
    '20.avi': [(2125, 1425), (2270, 1290)],
    '21.avi': [(1135, 1917), (1345, 764)],
    '22.avi': [(2195, 968), (1576, 486)],
    '23.avi': [(2195, 968), (1576, 486)],
    '24.avi': [(2195, 968), (1576, 486)],
    '25.avi': [(306, 1426), (2456, 1406)],
    '26.avi': [(230, 1420), (532, 949)],
    '27.avi': [(2064, 1039), (1603, 836)],
    '28.avi': [(2064, 1039), (1603, 836)],
    '29.avi': [(2064, 1039), (1603, 836)],
    '30.avi': [(2064, 1039), (1603, 836)],
    '31.avi': [(2064, 1039), (1603, 836)]
}