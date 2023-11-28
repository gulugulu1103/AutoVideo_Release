# 导入所需的库
import cv2
import numpy as np


def blur_resize(img_src: str, output_path: str, margin_pixels: int = 30, img_size: tuple = (2560, 1440),
                canvas_size: tuple = (3200, 1440)):
	# 加载原始图像
	img = cv2.imread(img_src)
	img_h, img_w = img_size
	canvas_h, canvas_w = canvas_size
	# 计算图像在画布中的位置
	img_start = canvas_h // 2 - img_h // 2
	img_end = img_start + img_h

	# 计算canvas图像上下的边缘
	margin_up = img_start
	margin_down = canvas_h - img_end

	# 对图像进行缩放
	img = cv2.resize(img, (img_w, img_h), interpolation = cv2.INTER_AREA)

	# 创建画布
	canvas = np.zeros((canvas_h, canvas_w, 3), dtype = np.uint8)

	# 将图像复制到画布的中间
	canvas[img_start:img_start + 2560, :] = img

	# 对画布上的边缘进行高斯模糊
	blur_up = cv2.resize(img[:margin_pixels, :], (canvas_w, margin_up), interpolation = cv2.INTER_AREA)
	canvas[:img_start, :] = cv2.GaussianBlur(blur_up, (51, 51), -0.1)

	# 对画布下边缘进行高斯模糊
	blur_down = cv2.resize(img[-margin_pixels:, :], (canvas_w, margin_down), interpolation = cv2.INTER_AREA)
	canvas[-margin_down:, :] = cv2.GaussianBlur(blur_down, (51, 51), -0.1)

	# 保存输出图像
	cv2.imwrite(output_path, canvas)


if __name__ == "__main__":
	blur_resize(r"/daily/2023_10_30/input/background.png",
	            "output.jpg")
