import cv2
import mmcv
import numpy as np
from shapely.geometry import Polygon
from mmsegmentation.mmseg.apis import inference_segmentor, init_segmentor
from scipy.spatial import distance as dist
import constants
import math

RIGHT = 1
LEFT = -1
ZERO = 0
  
def directionOfPoint(A, B, P):
    aX = A[0]
    aY = A[1]
    bX = B[0]
    bY = B[1]
    cX = P[0]
    cY = P[1]

    val = ((bX - aX)*(cY - aY) - (bY - aY)*(cX - aX))
    thresh = 0
    if val >= thresh:
        return LEFT
    elif val <= -thresh:
        return RIGHT
    else:
        return ZERO

def get_contact_point(p1, p2, center_point, cnt, _print = False):
    min_dist = 100000
    max_dist = 0
    ret = True
    min_contact_pt = None
    max_contact_pt = None
    contact_pt = None
    center_position = directionOfPoint(p1, p2, center_point)
    for ptt in cnt:
        pt = ptt[0]
        distance=int(np.linalg.norm(np.cross(p2-p1,pt-p1)/np.linalg.norm(p2-p1)))
        position = directionOfPoint(p1, p2, pt)
        if position * center_position >= 0:
            if distance < min_dist:
                min_dist = distance
                min_contact_pt = (pt[0], pt[1])
        else:
            min_dist = 0
            if distance > max_dist:
                max_dist = distance
                max_contact_pt = (pt[0], pt[1])
        if _print:
            print(position, center_position, p1, p2, pt, distance, min_dist, max_dist)
    if max_dist == 0 and min_dist == 0:
        return False, contact_pt, False

    if max_dist > 0:
        extend_flag = True
        contact_pt = max_contact_pt
    else:
        extend_flag = False
        contact_pt = min_contact_pt

    return ret, contact_pt, extend_flag

class DetectWorkspace:
    def __init__(self, wharf):
        self.config = constants.SEGMENTATION_CONFIG_PATH
        self.wharf = wharf
        if self.wharf == True:
            self.checkpoint = constants.SEGMENTATION_WHARF_MODEL_PATH
        else:
            self.checkpoint = constants.SEGMENTATION_MODEL_PATH
        self.model = init_segmentor(self.config, self.checkpoint, device="cuda:0")

    def detect_workspace_rect_hatch(self, frame, cnts):
        workspace_rects = []
        center_points = []
        direction = 0
        
        for cnt in cnts:
            hull = cv2.convexHull(cnt)
            
            rect = cv2.minAreaRect(hull)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            gray_image = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            mask = np.zeros_like(gray_image)
            cv2.drawContours(mask, [hull], 0, 255, -1) # Draw filled contour in mask
            out = np.zeros_like(gray_image) # Extract out the object and place into output image
            out[mask == 255] = gray_image[mask == 255]
            ordered_box = order_points(box)
            center_point = (int((ordered_box[0][0] + ordered_box[2][0]) / 2), int((ordered_box[0][1] + ordered_box[2][1]) / 2))
            center_points.append(center_point)

            blur = cv2.GaussianBlur(out, (5,5), 1)
            blur = blur.astype(np.float32)
            blur /=255.0
            kernelx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype = np.float32)
            kernely = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype = np.float32)
            gradient_x = cv2.filter2D(blur, -1, kernelx)
            gradient_y = cv2.filter2D(blur, -1, kernely)
            gradient_magnitude = np.hypot(gradient_x, gradient_y)
            dx = gradient_x*255.0
            dy = gradient_y*255.0
            dxx = np.interp(dx, (0, dx.max()), (0, 255))
            dyy = np.interp(dy, (0, dy.max()), (0, 255))
            _, dxx_thr = cv2.threshold(dxx, 50, 255, cv2.THRESH_TOZERO)
            _, dyy_thr = cv2.threshold(dyy, 50, 255, cv2.THRESH_TOZERO)
            x_sum = dxx_thr.sum()
            y_sum = dyy_thr.sum()
            print(x_sum, y_sum)
            if y_sum / x_sum >= 1.5:
                direction = 1

            print(f'direction {direction}')
            orientation = cv2.phase(dx, dy, angleInDegrees=True)
            thresh = 100
            _, binary_image = cv2.threshold(gradient_magnitude*255.0, thresh, 255, cv2.THRESH_BINARY)
            unit_degree = 360 / 20
            numbers_of_degree = []
            for i in range(20):
                n = np.sum((binary_image == 255) & (orientation >= unit_degree * i) & (orientation < unit_degree * (i + 1)))
                numbers_of_degree.append([i, n])
            
            arr_numbers_of_degree = np.array(numbers_of_degree)
            arr_numbers_of_degree = arr_numbers_of_degree[arr_numbers_of_degree[:, 1].argsort()[::-1][:20]] 
            real_angle_arr = []
            last_number = arr_numbers_of_degree[0][1]
            
            s0_1 = abs((ordered_box[2][1] - ordered_box[3][1])/(ordered_box[2][0] - ordered_box[3][0])) if ordered_box[2][0] - ordered_box[3][0] != 0 else -1
            s0_2 = abs((ordered_box[0][1] - ordered_box[3][1])/(ordered_box[0][0] - ordered_box[3][0])) if ordered_box[0][0] - ordered_box[3][0] != 0 else -1

            if direction == 0:    
                s0 = min(s0_1, s0_2) if s0_1 != -1 and s0_2 != -1 else max(s0_1, s0_2)
            else:
                s0 = max(s0_1, s0_2) if s0_1 != -1 and s0_2 != -1 else -1

            total_num = np.sum(arr_numbers_of_degree[:, 1])
            limit_num = total_num / 5

            for i in range(20):
                angle_idx = arr_numbers_of_degree[i][0]
                angle_count = arr_numbers_of_degree[i][1]
                
                if (total_num < limit_num or last_number / angle_count >= 2) and len(real_angle_arr) >= 2:
                    break
                total_num -= angle_count
                last_number = angle_count
                real_angle = angle_idx * unit_degree + 9 - 90

                if real_angle < 0:
                    real_angle += 180
                if real_angle >= 180:
                    real_angle -= 180

                s1 = np.tan(np.radians(real_angle))
                if s0 != -1:
                    ang = abs(angle(s1, s0))
                else:
                    ang = abs(real_angle - 90)

                if ang < 30:
                    continue

                if direction == 1:
                    real_angle = angle_idx * unit_degree + 9

                real_angle_arr.append(real_angle)

                if direction == 1 and len(real_angle_arr) >= 2:
                    break

            real_angle_arr.sort()
            count_real_angle_arr = len(real_angle_arr)

            if direction == 0:
                s1 = np.tan(np.radians(real_angle_arr[count_real_angle_arr - 1]))
                s2 = np.tan(np.radians(real_angle_arr[0]))

                if s0 == s0_1:
                    x = ordered_box[3][0] + 10 # top left
                    y = s1*(x - ordered_box[3][0]) + ordered_box[3][1]
                    x1, y1 = line_intersection(((x, y), ordered_box[3]), (ordered_box[0], ordered_box[1]))
                    x = ordered_box[2][0] + 10 # top left
                    y = s2*(x - ordered_box[2][0]) + ordered_box[2][1]
                    x2, y2 = line_intersection(((x, y), ordered_box[2]), (ordered_box[0], ordered_box[1]))
                    ordered_box[0] = (x1, y1)
                    ordered_box[1] = (x2, y2)
                else:
                    x = ordered_box[0][0] + 10 # top left
                    y = s1*(x - ordered_box[0][0]) + ordered_box[0][1]
                    x1, y1 = line_intersection(((x, y), ordered_box[0]), (ordered_box[1], ordered_box[2]))
                    x = ordered_box[3][0] + 10 # top left
                    y = s2*(x - ordered_box[3][0]) + ordered_box[3][1]
                    x2, y2 = line_intersection(((x, y), ordered_box[3]), (ordered_box[1], ordered_box[2]))
                    ordered_box[1] = (x1, y1)
                    ordered_box[2] = (x2, y2)
                ordered_box = order_points1(ordered_box)
                # print(x1, y1)
                # print(x2, y2)
            else:
                max_angle = real_angle_arr[count_real_angle_arr - 1] - 90
                min_angle = real_angle_arr[0] - 90
                max_angle = max_angle if max_angle >= 0 else max_angle + 180
                min_angle = min_angle if min_angle >= 0 else min_angle + 180
                max_angle = max_angle if max_angle >= 180 else max_angle - 180
                min_angle = min_angle if min_angle >= 180 else min_angle - 180
                s1 = np.tan(np.radians(max_angle))
                s2 = np.tan(np.radians(min_angle))
                ordered_box1 = ordered_box.copy()
                ordered_box2 = ordered_box.copy()
                if s0_2 == -1 or s0 == s0_2:
                    x = ordered_box[3][0] + 10 # top left
                    y = s2*(x - ordered_box[3][0]) + ordered_box[3][1]
                    x1, y1 = line_intersection(((x, y), ordered_box[3]), (ordered_box[1], ordered_box[2]))
                    x = ordered_box[0][0] + 10 # top left
                    y = s1*(x - ordered_box[0][0]) + ordered_box[0][1]
                    x2, y2 = line_intersection(((x, y), ordered_box[0]), (ordered_box[1], ordered_box[2]))
                    ordered_box1[2] = (x1, y1)
                    ordered_box1[1] = (x2, y2)
                else:
                    x = ordered_box[2][0] + 10 # top left
                    y = s2*(x - ordered_box[2][0]) + ordered_box[2][1]
                    x1, y1 = line_intersection(((x, y), ordered_box[2]), (ordered_box[1], ordered_box[0]))
                    x = ordered_box[3][0] + 10 # top left
                    y = s1*(x - ordered_box[3][0]) + ordered_box[3][1]
                    x2, y2 = line_intersection(((x, y), ordered_box[3]), (ordered_box[1], ordered_box[0]))
                    ordered_box1[1] = (x1, y1)
                    ordered_box1[0] = (x2, y2)
                ordered_box1 = order_points1(ordered_box1)

                if s0_2 == -1 or s0 == s0_2:
                    x = ordered_box[3][0] + 10 # top left
                    y = s1*(x - ordered_box[3][0]) + ordered_box[3][1]
                    x1, y1 = line_intersection(((x, y), ordered_box[3]), (ordered_box[1], ordered_box[0]))
                    x = ordered_box[2][0] + 10 # top left
                    y = s2*(x - ordered_box[2][0]) + ordered_box[2][1]
                    x2, y2 = line_intersection(((x, y), ordered_box[2]), (ordered_box[1], ordered_box[0]))
                    ordered_box2[0] = (x1, y1)
                    ordered_box2[1] = (x2, y2)
                else:
                    x = ordered_box[3][0] + 10 # top left
                    y = s2*(x - ordered_box[3][0]) + ordered_box[3][1]
                    x1, y1 = line_intersection(((x, y), ordered_box[3]), (ordered_box[1], ordered_box[2]))
                    x = ordered_box[0][0] + 10 # top left
                    y = s1*(x - ordered_box[0][0]) + ordered_box[0][1]
                    x2, y2 = line_intersection(((x, y), ordered_box[0]), (ordered_box[1], ordered_box[2]))
                    ordered_box2[2] = (x1, y1)
                    ordered_box2[1] = (x2, y2)
                ordered_box2 = order_points1(ordered_box2)

                polygon0 = Polygon(hull.squeeze()) # hull
                polygon1 = Polygon(ordered_box1) # approx
                polygon2 = Polygon(ordered_box2) # rotated_rect

                intersect1 = polygon1.intersection(polygon0).area
                union1 = polygon1.union(polygon0).area
                iou1 = intersect1 / union1

                intersect2 = polygon2.intersection(polygon0).area
                union2 = polygon2.union(polygon0).area
                iou2 = intersect2 / union2

                if iou1 > iou2:
                    ordered_box = ordered_box1
                else:
                    ordered_box = ordered_box2
            # print(f'  iou1 > iou2 {iou1 > iou2}')

            workspace_rects.append(ordered_box)

        return workspace_rects, center_points

    def segment_workspace(self, frame):
        frame_count = 0
        
        workspace_rects = []
        center_points = []
        workspace_contours = []
        if frame is None:
            return None, None

        result = inference_segmentor(self.model, frame)
        
        seg = result[0]
        color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)
        min_size = int(min(seg.shape[0], seg.shape[1]) / 10)
        color_seg[seg == 1, :] = [255, 0, 0]
        # mmcv.imwrite(color_seg, "out.png")
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (min_size,min_size))
        # color_seg = cv2.morphologyEx(color_seg, cv2.MORPH_OPEN, kernel)	
        color_seg = cv2.cvtColor(color_seg, cv2.COLOR_BGR2GRAY)
        cnts, hiers = cv2.findContours(color_seg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        area_max = 0
        new_cnts = []
        if not self.wharf:
            # eliminate too small cargo areas
            area_array = []
            for cnt in cnts:
                area = cv2.contourArea(cnt)
                area_array.append(area)
                if (area_max < area):
                    area_max = area

            thr_area = area_max // 5
            for i, cnt in enumerate(cnts):
                if area_array[i] > thr_area:
                    new_cnts.append(cnt)

            # workspace_rects, center_points = self.detect_workspace_rect_hatch(frame, new_cnts)
        else:
            #Find biggest contour
            biggest_cnt = []
            for cnt in cnts:
                area = cv2.contourArea(cnt)
                if (area_max < area):
                    area_max = area
                    biggest_cnt = cnt 
            new_cnts.append(biggest_cnt)

        approx_cnts = []
        for cnt in new_cnts:
            num_of_edge = len(cnt)
            approx = cnt
            rate = 0.0001
            while num_of_edge > 50:
                epsilon = rate*cv2.arcLength(cnt,True)
                approx = cv2.approxPolyDP(cnt,epsilon,True)
                num_of_edge = len(approx)
                rate += 0.0001
            cnt = approx
            approx_cnts.append(cnt)
            cv2.drawContours(color_seg, [cnt], -1, (0, 0, 255), 2)

        workspace_contours = approx_cnts

        if not self.wharf:
            workspace_rects, center_points = self.detect_workspace_rect_hatch(frame, approx_cnts)
            workspace_rects, workspace_contours = optimize_workspace_rects(workspace_rects, workspace_contours)
    
        if self.wharf:
            workspace_rects = workspace_contours
            
        return workspace_rects, center_points, workspace_contours

def optimize_workspace_rects(rects, contours):
    for i, rect in enumerate(rects):
        center_x, center_y = line_intersection((rect[0], rect[2]), (rect[1], rect[3]))
        ret_bottom, pt_bottom, extend_bottom = get_contact_point(rect[0], rect[1], [center_x, center_y], contours[i])
        ret_right, pt_right, extend_right = get_contact_point(rect[1], rect[2], [center_x, center_y], contours[i])
        ret_top, pt_top, extend_top = get_contact_point(rect[2], rect[3], [center_x, center_y], contours[i])
        ret_left, pt_left, extend_left = get_contact_point(rect[3], rect[0], [center_x, center_y], contours[i])
        # print(ret_bottom, ret_right, ret_top, ret_left)
        # print(extend_bottom, extend_right, extend_top, extend_left)
        if ret_left:
            pt = line_intersection((rect[0], rect[3]), ((pt_left[0] - 10, pt_left[1]), pt_left))
            left_offset = math.dist(pt, pt_left)
            tmp_0, tmp_3 = rect[0].copy(), rect[3].copy()
            if extend_left:
                tmp_0[0] -= left_offset
                tmp_3[0] -= left_offset
            else:
                tmp_0[0] += left_offset
                tmp_3[0] += left_offset
            rect[3] = line_intersection((rect[2], rect[3]), (tmp_0, tmp_3))
            rect[0] = line_intersection((rect[0], rect[1]), (tmp_0, tmp_3))
        
        if ret_right:
            pt = line_intersection((rect[1], rect[2]), ((pt_right[0] - 10, pt_right[1]), pt_right))
            right_offset = math.dist(pt, pt_right)
            tmp_1, tmp_2 = rect[1].copy(), rect[2].copy()
            if extend_right:
                tmp_1[0] += right_offset
                tmp_2[0] += right_offset
            else:
                tmp_1[0] -= right_offset
                tmp_2[0] -= right_offset
            rect[2] = line_intersection((rect[2], rect[3]), (tmp_1, tmp_2))
            rect[1] = line_intersection((rect[0], rect[1]), (tmp_1, tmp_2))
        
        if ret_top:
            pt = line_intersection((rect[2], rect[3]), ((pt_top[0], pt_top[1] + 10), pt_top))
            top_offset = math.dist(pt, pt_top)
            tmp_2, tmp_3 = rect[2].copy(), rect[3].copy()
            if extend_top:
                tmp_2[1] -= top_offset
                tmp_3[1] -= top_offset
            else:
                tmp_2[1] += top_offset
                tmp_3[1] += top_offset
            rect[3] = line_intersection((rect[0], rect[3]), (tmp_2, tmp_3))
            rect[2] = line_intersection((rect[2], rect[1]), (tmp_2, tmp_3))

        if ret_bottom:
            pt = line_intersection((rect[1], rect[0]), ((pt_bottom[0], pt_bottom[1] + 10), pt_bottom))
            bottom_offset = math.dist(pt, pt_bottom)
            tmp_0, tmp_1 = rect[0].copy(), rect[1].copy()
            if extend_bottom:
                tmp_0[1] += bottom_offset
                tmp_1[1] += bottom_offset
            else:
                tmp_0[1] -= bottom_offset
                tmp_1[1] -= bottom_offset
            rect[0] = line_intersection((rect[0], rect[3]), (tmp_1, tmp_0))
            rect[1] = line_intersection((rect[2], rect[1]), (tmp_1, tmp_0))
        rects[i] = rect
    return rects, contours



def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]
    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]
    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([bl, br, tr, tl], dtype="float32")

def order_points1(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]
    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    
    (tr, br) = rightMost[np.argsort(rightMost[:, 1]), :]


    v1 = [bl[0]-br[0], bl[1]-br[1]]   # Vector 1
    v2 = [tl[0]-br[0], tl[1]-br[1]]   # Vector 2
    v3 = [tr[0]-br[0], tr[1]-br[1]]   # Vector 3
    cross_product1 = v1[0]*v2[1] - v1[1]*v2[0]
    cross_product2 = v1[0]*v3[1] - v1[1]*v3[0]
    if cross_product1 < 0:
        print('cross_product1 < 0')
        tmp = tl, bl
        bl = tmp[0]
        tl = tmp[1]

    if cross_product2 < 0:
        print('cross_product2 < 0')
        tmp = tr, br
        br = tmp[0]
        tr = tmp[1]
    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order


    return np.array([bl, br, tr, tl], dtype="float32")

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return int(x), int(y)

def slope(x1, y1, x2, y2): # Line slope given two points:
    return (y2-y1)/(x2-x1)

def angle(s1, s2): 
    return math.degrees(math.atan((s2-s1)/(1+(s2*s1))))