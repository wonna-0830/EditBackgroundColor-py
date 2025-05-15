import tkinter as tk
import cv2
import numpy as np
from fpdf import FPDF

# 메인 화면 만들기(버튼)
window = tk.Tk()
window.title("배경 색 바꾸기")
window.geometry("600x400+{}+{}".format((window.winfo_screenwidth() - 600) // 2, (window.winfo_screenheight() - 400) // 2))

# RGB 값 정의
color_dict = {
    'purple': (255, 192, 203),
    'yellow': (135, 206, 235),
    'pink': (203, 192, 255),
    'gray': (128, 128, 128),
    'blue': (255, 192, 148)
}

# 버튼 클릭이벤트
def button_click(button_color):
    # 이미지 로드
    image = cv2.imread('images/picture.jpg')

    # 이니셜 마스크 만들기
    mask = np.zeros(image.shape[:2], np.uint8)

    # 백그라운드, 포어그라운드 정의
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # 직사각형 생성
    rect = (50, 50, image.shape[1] - 100, image.shape[0] - 100)

    # grabcut 알고리즘 적용
    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    # 수동으로 명치 부분을 전경으로 설정 (이 부분을 더 정교하게 수정)
    mask[1140:, :1300] = cv2.GC_FGD
    mask[300:600, 400:780] = cv2.GC_FGD
    # 여기에 원을 추가하여 특정 부분을 전경으로 설정
    center = (150, 1200)  # 원의 중심 좌표를 지정 (x, y)
    radius = 167 # 원의 반지름
    cv2.circle(mask, center, radius, cv2.GC_FGD, -1)  # 원 안쪽을 전경으로 설정

    center = (969, 1200)  # 원의 중심 좌표를 지정 (x, y)
    radius = 167  # 원의 반지름
    cv2.circle(mask, center, radius, cv2.GC_FGD, -1)  # 원 안쪽을 전경으로 설정

    # grabcut 알고리즘을 다시 적용
    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

    # 수동으로 잘못된 부분을 수정 (예: 명치 부분)
    new_mask = np.copy(mask)
    new_mask[mask == cv2.GC_PR_BGD] = cv2.GC_BGD  # 잠재적 배경을 배경으로 설정
    new_mask[mask == cv2.GC_PR_FGD] = cv2.GC_FGD  # 잠재적 전경을 전경으로 설정

    # grabcut 알고리즘을 다시 적용
    cv2.grabCut(image, new_mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

    # 전경 이외에는 모든 픽셀을 0으로 설정
    mask2 = np.where((new_mask == 2) | (new_mask == 0), 0, 1).astype('uint8')

    # 전경, 배경 구분
    foreground = image * mask2[:, :, np.newaxis]

    # 클릭한 버튼 색으로 배경 변경하기
    background = np.ones_like(image, np.uint8) * color_dict[button_color]

    # 전경과 배경 합치기
    result = background * (1 - mask2[:, :, np.newaxis]) + foreground

    # 이미지 데이터 유형을 unit8로 변경
    if result.dtype != np.uint8:
        result = result.astype(np.uint8)

    # 결과를 임시 이미지 파일로 저장
    temp_filename = 'temp_result.jpg'
    cv2.imwrite(temp_filename, result)

    # PDF로 저장
    pdf = FPDF()
    pdf.add_page()
    pdf.image(temp_filename, x=10, y=10, w=190)
    pdf_filename = f'output_{button_color}.pdf'
    pdf.output(pdf_filename, 'F')

    # 이미지 크기를 원본의 50퍼센트로 줄이기
    resized_result = cv2.resize(result, (0, 0), fx=0.5, fy=0.5)

    # 줄인 이미지를 표시
    cv2.imshow('Image', resized_result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 버튼 생성
for color in ['purple', 'yellow', 'pink', 'gray', 'blue']:
    button = tk.Button(window, width=20, height=2, padx=10, pady=20, text=color, command=lambda c=color: button_click(c))
    button.pack()

# 창의 주 루프 실행
window.mainloop()
