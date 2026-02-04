from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import cv2
import shutil
import numpy as np
import math
import random
import os
import tkinter.font as tkFont
import matplotlib.pyplot as plt

np.set_printoptions(suppress=True)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ============ 通用工具函数 ============
def plus(s):
    """填充8位二进制"""
    return bin(s).replace('0b', '').zfill(8)


def get_key(file_path):
    """读取文件并转换为二进制字符串"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        binary_str = ""
        for byte in data:
            binary_str += plus(byte)

        global text_len
        text_len = len(data)  # 字节数
        return binary_str
    except Exception as e:
        tkinter.messagebox.showerror('错误', f'读取文件失败:\n{str(e)}')
        return ""


def mod(x, y):
    """取模运算"""
    return x % y


def toasc(binary_str):
    """二进制字符串转换为整数"""
    return int(binary_str, 2)


def q_converto_wh_fixed(q, image_width):
    """
    安全坐标转换函数
    q: 一维索引（从1开始）
    image_width: 图像宽度
    返回: (row, col) 行和列
    """
    if q <= 0:
        return 0, 0

    # 转换为0-based索引
    index = q - 1

    # 计算行列
    row = index // image_width
    col = index % image_width

    return row, col


def check_and_convert_image(image_path, save_converted=False):
    """
    检查和转换图像模式
    返回: PIL Image对象
    """
    img = Image.open(image_path)

    # 显示图像信息
    print(f"图像信息: 模式={img.mode}, 尺寸={img.size}, 格式={img.format}")

    # 处理不同模式
    if img.mode == '1':  # 1-bit像素
        img = img.convert('RGB')
    elif img.mode == 'L':  # 灰度
        img = img.convert('RGB')
    elif img.mode == 'P':  # 调色板
        img = img.convert('RGB')
    elif img.mode == 'RGBA':  # RGBA
        # 创建白色背景，将RGBA粘贴到RGB上
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3] if len(img.split()) >= 4 else None)
        img = rgb_img
    elif img.mode not in ['RGB', 'CMYK']:
        # 其他模式转换为RGB
        img = img.convert('RGB')

    # 如果需要保存转换后的图像
    if save_converted and not image_path.lower().endswith(('.bmp', '.png')):
        converted_path = image_path.rsplit('.', 1)[0] + '_converted.png'
        img.save(converted_path, 'PNG')
        return img, converted_pathze

    return img, image_path


def show_image_comparison(original_path, modified_path, title1="原始图像", title2="隐写后图像"):
    """显示原始图像和修改后图像的对比"""
    try:
        # 使用PIL读取图像
        original_img = Image.open(original_path)
        modified_img = Image.open(modified_path)

        # 转换为numpy数组
        original_array = np.array(original_img)
        modified_array = np.array(modified_img)

        # 确保是RGB
        if len(original_array.shape) == 2:  # 灰度图
            original_array = np.stack([original_array] * 3, axis=2)
        if len(modified_array.shape) == 2:
            modified_array = np.stack([modified_array] * 3, axis=2)

        # 创建对比图
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        # 原始图像
        axes[0, 0].imshow(original_array)
        axes[0, 0].set_title(title1)
        axes[0, 0].axis('off')

        # 原始图像直方图
        axes[0, 1].hist(original_array.ravel(), 256, [0, 256])
        axes[0, 1].set_title(f'{title1}直方图')
        axes[0, 1].set_xlabel('像素值')
        axes[0, 1].set_ylabel('频次')

        # 隐写后图像
        axes[1, 0].imshow(modified_array)
        axes[1, 0].set_title(title2)
        axes[1, 0].axis('off')

        # 隐写后图像直方图
        axes[1, 1].hist(modified_array.ravel(), 256, [0, 256])
        axes[1, 1].set_title(f'{title2}直方图')
        axes[1, 1].set_xlabel('像素值')
        axes[1, 1].set_ylabel('频次')

        plt.suptitle('图像隐写对比', fontsize=16)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"显示图像对比时出错: {e}")
        tkinter.messagebox.showwarning('警告', '无法显示图像对比图')


# ============ 基本LSB隐写算法 ============
def func_LSB_basic_yinxie(str1, str2, str3):
    """基本LSB隐写"""
    try:
        # 检查和转换图像
        im, converted_path = check_and_convert_image(str1, save_converted=True)
        if im is None:
            return

        width, height = im.size
        total_pixels = width * height

        print(f"图像尺寸: {width}x{height}, 总像素: {total_pixels}")

        # 获取要隐藏的信息
        key = get_key(str2)
        if not key:
            return

        keylen = len(key)
        print(f"密钥长度: {keylen} bits {keylen / 8} 位")

        # 检查容量
        if keylen > total_pixels * 3:  # 每个像素有3个通道
            tkinter.messagebox.showerror('错误',
                                         f'图像容量不足！\n需要: {keylen}位\n可用: {total_pixels * 3}位')
            return

        # 嵌入信息
        count = 0
        modified_count = 0

        for h in range(height):
            for w in range(width):
                if count >= keylen:
                    break

                pixel = im.getpixel((w, h))

                # 处理RGB通道
                if isinstance(pixel, int):  # 灰度图像
                    a = pixel
                    if count < keylen:
                        a = a - mod(a, 2) + int(key[count])
                        count += 1
                        modified_count += 1
                        im.putpixel((w, h), a)
                else:  # RGB图像
                    r, g, b = pixel[:3]

                    # 红色通道
                    if count < keylen:
                        r = r - mod(r, 2) + int(key[count])
                        count += 1
                        modified_count += 1

                    # 绿色通道
                    if count < keylen:
                        g = g - mod(g, 2) + int(key[count])
                        count += 1
                        modified_count += 1

                    # 蓝色通道
                    if count < keylen:
                        b = b - mod(b, 2) + int(key[count])
                        count += 1
                        modified_count += 1

                    # 更新像素
                    if len(pixel) > 3:  # 如果有alpha通道
                        im.putpixel((w, h), (r, g, b, pixel[3]))
                    else:
                        im.putpixel((w, h), (r, g, b))

            if count >= keylen:
                break

        print(f"成功修改了 {modified_count} 个像素值")

        # 确保输出为PNG格式
        if not str3.lower().endswith('.png'):
            str3 = str3.rsplit('.', 1)[0] + '.png'

        # 保存图像
        im.save(str3, 'PNG')
        tkinter.messagebox.showinfo('成功',
                                    f'基本LSB隐写完成！\n'
                                    f'修改了 {modified_count} 个像素值\n'
                                    f'保存为: {str3}')

        # 显示对比
        show_image_comparison(converted_path if converted_path != str1 else str1,
                              str3, "原始图像", "基本LSB隐写后图像")

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'基本LSB隐写失败:\n{str(e)}')
        print(f"详细错误: {e}")


def LSB_basic_yinxie():
    """基本LSB隐写GUI入口"""
    tkinter.messagebox.showinfo('提示', '请选择要进行基本LSB隐写的图像')
    Fpath = filedialog.askopenfilename()

    if not Fpath:
        return

    # 检查格式并提示
    if Fpath.lower().endswith(('.jpg', '.jpeg')):
        tkinter.messagebox.showwarning('注意',
                                       'JPG格式有损压缩可能影响隐写效果，\n程序将自动转换为PNG格式处理')

    # 处理后输出的图片路径
    filename = os.path.basename(Fpath)
    name_part = filename.rsplit('.', 1)[0]
    new = f"{name_part}_LSB_basic.png"

    # 需要隐藏的信息
    tkinter.messagebox.showinfo('提示', '请选择要隐藏的信息(txt文件)')
    txtpath = filedialog.askopenfilename()

    if not txtpath:
        return

    func_LSB_basic_yinxie(Fpath, txtpath, new)


def func_LSB_basic_tiqu(le, str1, str2):
    """基本LSB提取"""
    try:
        # 打开图像
        im, _ = check_and_convert_image(str1)
        if im is None:
            return

        width, height = im.size

        # 检查提取长度
        if le * 8 > width * height * 3:
            tkinter.messagebox.showerror('错误', '提取长度超过图像容量')
            return

        # 计算实际需要提取的位数
        bits_needed = le * 8

        # 提取信息
        count = 0
        binary_str = ""

        for h in range(height):
            for w in range(width):
                if count >= bits_needed:
                    break

                pixel = im.getpixel((w, h))

                if isinstance(pixel, int):  # 灰度图像
                    if count < bits_needed:
                        binary_str += str(mod(pixel, 2))
                        count += 1
                else:  # RGB图像
                    # 红色通道
                    if count < bits_needed:
                        binary_str += str(mod(pixel[0], 2))
                        count += 1

                    # 绿色通道
                    if count < bits_needed:
                        binary_str += str(mod(pixel[1], 2))
                        count += 1

                    # 蓝色通道
                    if count < bits_needed:
                        binary_str += str(mod(pixel[2], 2))
                        count += 1

            if count >= bits_needed:
                break

        print(f"提取到 {len(binary_str)} 位二进制数据")

        # 将二进制转换为字节并保存
        with open(str2, "wb") as f:
            for i in range(0, len(binary_str), 8):
                if i + 8 <= len(binary_str):
                    byte_str = binary_str[i:i + 8]
                    byte_value = toasc(byte_str)
                    f.write(bytes([byte_value]))

        tkinter.messagebox.showinfo('成功', f'信息提取完成，保存到: {str2}')

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'基本LSB提取失败:\n{str(e)}')


global LSB_basic_text_len
LSB_basic_text_len = 100


def LSB_basic_tiqu():
    """基本LSB提取GUI入口"""
    # 获取提取长度
    global LSB_basic_text_len
    try:
        le = int(LSB_basic_text_len)
    except:
        tkinter.messagebox.showerror('错误', '请先设置提取信息的长度')
        return

    tkinter.messagebox.showinfo('提示', '请选择要进行基本LSB算法提取的图像')
    Fpath = filedialog.askopenfilename()

    if not Fpath:
        return

    tkinter.messagebox.showinfo('提示', '请选择将提取信息保存的位置')
    tiqu = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not tiqu:
        return

    func_LSB_basic_tiqu(le, Fpath, tiqu)


# ============ LSB随机间隔算法 ============
global LSB_suijijiange_step
LSB_suijijiange_step = 2


def func_LSB_suijijiange_yinxie(str1, str2, str3):
    """LSB随机间隔隐写"""
    try:
        # 检查和转换图像
        im, converted_path = check_and_convert_image(str1, save_converted=True)
        if im is None:
            return

        width, height = im.size
        total_pixels = width * height

        print(f"图像尺寸: {width}x{height}, 总像素: {total_pixels}")

        # 获取要隐藏的信息
        key = get_key(str2)
        if not key:
            return

        keylen = len(key)
        print(f"密钥长度: {keylen} bits {keylen / 8} 位")

        # 检查容量
        if keylen > total_pixels:
            tkinter.messagebox.showerror('错误',
                                         f'图像容量不足！\n需要: {keylen}像素\n可用: {total_pixels}像素')
            return

        # 检查步长
        global LSB_suijijiange_step
        step = int(LSB_suijijiange_step)
        step_max = max(1, total_pixels // keylen)

        if step > step_max:
            tkinter.messagebox.showwarning('警告',
                                           f'步长设置过大，自动调整为最大步长: {step_max}')
            step = step_max

        # 生成随机序列
        random.seed(2)  # 固定随机种子以便提取
        random_seq = [int(random.random() * step + 1) for _ in range(keylen)]

        # 嵌入信息
        q = 1
        modified_count = 0

        for i in range(keylen):
            # 检查是否超出图像范围
            if q > total_pixels:
                tkinter.messagebox.showwarning('警告',
                                               f'只能嵌入 {modified_count}/{keylen} 位信息')
                break

            # 计算坐标
            row, col = q_converto_wh_fixed(q, width)

            # 验证坐标
            if row >= height or col >= width:
                print(f"警告: 坐标({row},{col})超出范围({height},{width})")
                q += random_seq[i]
                continue

            # 获取像素值
            pixel = im.getpixel((col, row))

            # 根据像素类型处理
            if isinstance(pixel, int):  # 灰度图像
                new_pixel = pixel - mod(pixel, 2) + int(key[i])
            else:  # RGB图像
                r, g, b = pixel[:3]  # 只取前三个通道
                new_r = r - mod(r, 2) + int(key[i])
                new_pixel = (new_r, g, b) + pixel[3:] if len(pixel) > 3 else (new_r, g, b)

            # 更新像素
            im.putpixel((col, row), new_pixel)
            modified_count += 1

            # 移动到下一个位置
            q += random_seq[i]

        print(f"成功修改了 {modified_count} 个像素")

        # 确保输出为PNG格式
        if not str3.lower().endswith('.png'):
            str3 = str3.rsplit('.', 1)[0] + '.png'

        # 保存图像
        im.save(str3, 'PNG')
        tkinter.messagebox.showinfo('成功',
                                    f'LSB随机间隔隐写完成！\n'
                                    f'修改了 {modified_count} 个像素\n'
                                    f'保存为: {str3}')

        # 显示对比
        show_image_comparison(converted_path if converted_path != str1 else str1,
                              str3, "原始图像", "LSB随机间隔隐写后图像")

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'LSB随机间隔隐写失败:\n{str(e)}')
        print(f"详细错误: {e}")


def LSB_suijijiange_yinxie():
    """LSB随机间隔隐写GUI入口"""
    tkinter.messagebox.showinfo('提示', '请选择要进行LSB随机间隔隐写的图像')
    Fpath = filedialog.askopenfilename()

    if not Fpath:
        return

    # 检查格式并提示
    if Fpath.lower().endswith(('.jpg', '.jpeg')):
        tkinter.messagebox.showwarning('注意',
                                       'JPG格式有损压缩可能影响隐写效果，\n程序将自动转换为PNG格式处理')

    # 处理后输出的图片路径
    filename = os.path.basename(Fpath)
    name_part = filename.rsplit('.', 1)[0]
    new = f"{name_part}_LSB_random_interval.png"

    # 需要隐藏的信息
    tkinter.messagebox.showinfo('提示', '请选择要隐藏的信息(txt文件)')
    txtpath = filedialog.askopenfilename()

    if not txtpath:
        return

    func_LSB_suijijiange_yinxie(Fpath, txtpath, new)


def func_LSB_suijijiange_tiqu(le, str1, str2):
    """LSB随机间隔提取"""
    try:
        # 打开图像
        im, _ = check_and_convert_image(str1)
        if im is None:
            return

        width, height = im.size
        total_pixels = width * height

        # 检查提取长度
        if le * 8 > total_pixels:
            tkinter.messagebox.showerror('错误', '提取长度超过图像容量')
            return

        # 计算实际需要提取的位数
        bits_needed = le * 8

        # 生成随机序列（必须与嵌入时相同）
        global LSB_suijijiange_step
        step = int(LSB_suijijiange_step)
        random.seed(2)
        random_seq = [int(random.random() * step + 1) for _ in range(bits_needed)]

        # 提取信息
        q = 1
        binary_str = ""

        for i in range(bits_needed):
            if q > total_pixels:
                tkinter.messagebox.showwarning('警告', '提取信息不完整')
                break

            # 计算坐标
            row, col = q_converto_wh_fixed(q, width)

            # 检查坐标
            if row >= height or col >= width:
                q += random_seq[i]
                continue

            # 获取像素
            pixel = im.getpixel((col, row))

            # 提取LSB
            if isinstance(pixel, int):  # 灰度
                binary_str += str(mod(pixel, 2))
            else:  # RGB
                binary_str += str(mod(pixel[0], 2))  # 提取红色通道的LSB

            # 移动到下一个位置
            q += random_seq[i]

        print(f"提取到 {len(binary_str)} 位二进制数据")

        # 将二进制转换为字节并保存
        with open(str2, "wb") as f:
            for i in range(0, len(binary_str), 8):
                if i + 8 <= len(binary_str):
                    byte_str = binary_str[i:i + 8]
                    byte_value = toasc(byte_str)
                    f.write(bytes([byte_value]))

        tkinter.messagebox.showinfo('成功', f'信息提取完成，保存到: {str2}')

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'LSB随机间隔提取失败:\n{str(e)}')


global LSB_suijijiange_text_len
LSB_suijijiange_text_len = 100


def LSB_suijijiange_tiqu():
    """LSB随机间隔提取GUI入口"""
    # 获取提取长度
    global LSB_suijijiange_text_len
    try:
        le = int(LSB_suijijiange_text_len)
    except:
        tkinter.messagebox.showerror('错误', '请先设置提取信息的长度')
        return

    tkinter.messagebox.showinfo('提示', '请选择要进行LSB随机间隔算法提取的图像')
    Fpath = filedialog.askopenfilename()

    if not Fpath:
        return

    tkinter.messagebox.showinfo('提示', '请选择将提取信息保存的位置')
    tiqu = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not tiqu:
        return

    func_LSB_suijijiange_tiqu(le, Fpath, tiqu)


# ============ LSB区域校验位算法 ============
global LSB_quyujiaoyan_size
LSB_quyujiaoyan_size = 4


def func_LSB_quyujiaoyan_yinxie(str1, str2, str3):
    """LSB区域校验位隐写"""
    try:
        # 检查和转换图像
        im, converted_path = check_and_convert_image(str1, save_converted=True)
        if im is None:
            return

        width, height = im.size
        total_pixels = width * height

        # 获取要隐藏的信息
        key = get_key(str2)
        if not key:
            return

        keylen = len(key)

        # 检查区域大小
        global LSB_quyujiaoyan_size
        size = int(LSB_quyujiaoyan_size)

        # 检查容量
        if keylen * size > total_pixels:
            tkinter.messagebox.showerror('错误',
                                         f'图像容量不足！\n需要: {keylen * size}像素\n可用: {total_pixels}像素')
            return

        # 嵌入信息
        for p in range(keylen):
            # 计算区域像素的LSB总和
            lsb_sum = 0
            pixels_to_modify = []

            for i in range(1, size + 1):
                # 计算一维索引
                q = p * size + i
                if q > total_pixels:
                    break

                # 计算坐标
                row, col = q_converto_wh_fixed(q, width)

                # 检查坐标
                if row < height and col < width:
                    pixel = im.getpixel((col, row))

                    if isinstance(pixel, int):  # 灰度
                        lsb_sum += mod(pixel, 2)
                    else:  # RGB
                        lsb_sum += mod(pixel[0], 2)  # 红色通道

                    pixels_to_modify.append((col, row))

            # 计算校验位
            current_check = mod(lsb_sum, 2)
            target_check = int(key[p])

            # 如果校验位不匹配，修改一个像素
            if current_check != target_check and pixels_to_modify:
                # 随机选择一个像素修改
                col, row = random.choice(pixels_to_modify)
                pixel = im.getpixel((col, row))

                if isinstance(pixel, int):  # 灰度
                    new_pixel = pixel ^ 1  # 翻转LSB
                else:  # RGB
                    r, g, b = pixel[:3]
                    new_pixel = (r ^ 1, g, b) + pixel[3:] if len(pixel) > 3 else (r ^ 1, g, b)

                im.putpixel((col, row), new_pixel)

        # 保存图像
        if not str3.lower().endswith('.png'):
            str3 = str3.rsplit('.', 1)[0] + '.png'

        im.save(str3, 'PNG')
        tkinter.messagebox.showinfo('成功',
                                    f'LSB区域校验位隐写完成！\n保存为: {str3}')

        # 显示对比
        show_image_comparison(converted_path if converted_path != str1 else str1,
                              str3, "原始图像", "LSB区域校验位隐写后图像")

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'LSB区域校验位隐写失败:\n{str(e)}')


def LSB_quyujiaoyan_yinxie():
    """LSB区域校验位隐写GUI入口"""
    tkinter.messagebox.showinfo('提示', '请选择要进行LSB区域校验位隐写的图像')
    Fpath = filedialog.askopenfilename()

    if not Fpath:
        return

    # 检查格式并提示
    if Fpath.lower().endswith(('.jpg', '.jpeg')):
        tkinter.messagebox.showwarning('注意',
                                       'JPG格式有损压缩可能影响隐写效果，\n程序将自动转换为PNG格式处理')

    # 处理后输出的图片路径
    filename = os.path.basename(Fpath)
    name_part = filename.rsplit('.', 1)[0]
    new = f"{name_part}_LSB_regional_verification.png"

    # 需要隐藏的信息
    tkinter.messagebox.showinfo('提示', '请选择要隐藏的信息(txt文件)')
    txtpath = filedialog.askopenfilename()

    if not txtpath:
        return

    func_LSB_quyujiaoyan_yinxie(Fpath, txtpath, new)


def func_LSB_quyujiaoyan_tiqu(le, str1, str2):
    """LSB区域校验位提取"""
    try:
        # 打开图像
        im, _ = check_and_convert_image(str1)
        if im is None:
            return

        width, height = im.size
        total_pixels = width * height

        # 检查区域大小
        global LSB_quyujiaoyan_size
        size = int(LSB_quyujiaoyan_size)

        # 检查容量
        if le * 8 * size > total_pixels:
            tkinter.messagebox.showerror('错误', '提取长度超过图像容量')
            return

        # 提取信息
        binary_str = ""
        total_bits = le * 8

        for p in range(total_bits):
            # 计算区域像素的LSB总和
            lsb_sum = 0

            for i in range(1, size + 1):
                # 计算一维索引
                q = p * size + i
                if q > total_pixels:
                    break

                # 计算坐标
                row, col = q_converto_wh_fixed(q, width)

                # 检查坐标
                if row < height and col < width:
                    pixel = im.getpixel((col, row))

                    if isinstance(pixel, int):  # 灰度
                        lsb_sum += mod(pixel, 2)
                    else:  # RGB
                        lsb_sum += mod(pixel[0], 2)  # 红色通道

            # 计算校验位
            check_bit = mod(lsb_sum, 2)
            binary_str += str(check_bit)

        print(f"提取到 {len(binary_str)} 位二进制数据")

        # 将二进制转换为字节并保存
        with open(str2, "wb") as f:
            for i in range(0, len(binary_str), 8):
                if i + 8 <= len(binary_str):
                    byte_str = binary_str[i:i + 8]
                    byte_value = toasc(byte_str)
                    f.write(bytes([byte_value]))

        tkinter.messagebox.showinfo('成功', f'信息提取完成，保存到: {str2}')

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'LSB区域校验位提取失败:\n{str(e)}')


global LSB_quyujiaoyan_text_len
LSB_quyujiaoyan_text_len = 100


def LSB_quyujiaoyan_tiqu():
    """LSB区域校验位提取GUI入口"""
    # 获取提取长度
    global LSB_quyujiaoyan_text_len
    try:
        le = int(LSB_quyujiaoyan_text_len)
    except:
        tkinter.messagebox.showerror('错误', '请先设置提取信息的长度')
        return

    tkinter.messagebox.showinfo('提示', '请选择要进行LSB区域校验位算法提取的图像')
    Fpath = filedialog.askopenfilename()

    if not Fpath:
        return

    tkinter.messagebox.showinfo('提示', '请选择将提取信息保存的位置')
    tiqu = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not tiqu:
        return

    func_LSB_quyujiaoyan_tiqu(le, Fpath, tiqu)


# ============ 基本图像降级算法 ============
def Image_basic_yinxie():
    """基本图像降级隐写（对比用）"""
    try:
        # 选择载体图像
        tkinter.messagebox.showinfo('提示', '请选择载体图像')
        Fpath1 = filedialog.askopenfilename()

        if not Fpath1:
            return

        # 选择水印图像
        tkinter.messagebox.showinfo('提示', '请选择要隐写的水印图像')
        Fpath2 = filedialog.askopenfilename()

        if not Fpath2:
            return

        # 打开并检查图像
        img, _ = check_and_convert_image(Fpath1)
        mark, _ = check_and_convert_image(Fpath2)

        if img is None or mark is None:
            return

        # 转换为numpy数组
        img_array = np.array(img)
        mark_array = np.array(mark)

        # 检查尺寸 - 载体图像需要是水印图像的2倍
        if len(mark_array.shape) == 2:  # 灰度水印
            mark_rows, mark_cols = mark_array.shape
            mark_dims = 1
        else:  # 彩色水印
            mark_rows, mark_cols, mark_dims = mark_array.shape

        if len(img_array.shape) == 2:  # 灰度载体
            img_rows, img_cols = img_array.shape
            img_dims = 1
        else:  # 彩色载体
            img_rows, img_cols, img_dims = img_array.shape

        # 检查载体图像是否足够大（至少是水印图像的2倍）
        if img_rows < mark_rows * 2 or img_cols < mark_cols * 2:
            tkinter.messagebox.showerror('错误',
                                         f'载体图像太小！\n'
                                         f'载体图像尺寸: {img_cols}x{img_rows}\n'
                                         f'水印图像需要载体尺寸至少为: {mark_cols * 2}x{mark_rows * 2}')
            return

        print(f"载体图像: {img_cols}x{img_rows}, 通道数: {img_dims}")
        print(f"水印图像: {mark_cols}x{mark_rows}, 通道数: {mark_dims}")

        # 基本图像降级算法：将水印图像的高4位嵌入到载体图像的低4位
        # 清空载体图像的最低4位 (240 = 11110000)
        img_array = img_array & 240

        # 将水印图像的高4位嵌入到载体图像的低4位
        for i in range(min(mark_dims, img_dims)):  # 处理每个通道
            for j in range(mark_rows):
                for k in range(mark_cols):
                    # 获取水印像素值
                    if mark_dims == 1:  # 灰度图像
                        mark_pixel = mark_array[j, k]
                    else:  # 彩色图像
                        mark_pixel = mark_array[j, k, i]

                    # 计算载体图像中的位置（2x2块中的左上角）
                    img_j = j * 2
                    img_k = k * 2

                    # 确保坐标在范围内
                    if img_j < img_rows and img_k < img_cols:
                        # 将水印像素的高4位（240 = 11110000）嵌入到载体像素的低4位
                        watermark_bits = (mark_pixel & 240) >> 4  # 取高4位

                        if img_dims == 1:  # 灰度载体
                            img_array[img_j, img_k] = img_array[img_j, img_k] + watermark_bits
                        else:  # 彩色载体
                            img_array[img_j, img_k, i] = img_array[img_j, img_k, i] + watermark_bits

        # 保存结果
        result_img = Image.fromarray(img_array)
        filename = os.path.basename(Fpath1)
        name_part = filename.rsplit('.', 1)[0]
        output_path = f"{name_part}_with_watermark_basic.png"

        result_img.save(output_path, 'PNG')
        tkinter.messagebox.showinfo('成功',
                                    f'基本图像降级隐写完成！\n'
                                    f'载体图像: {img_cols}x{img_rows}\n'
                                    f'水印图像: {mark_cols}x{mark_rows}\n'
                                    f'保存为: {output_path}')

        # 显示对比
        show_image_comparison(Fpath1, output_path, "原始图像", "基本图像降级隐写后图像")

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'基本图像降级隐写失败:\n{str(e)}')
        print(f"详细错误: {e}")
        import traceback
        traceback.print_exc()


def Image_basic_tiqu():
    """基本图像降级提取"""
    try:
        # 选择隐写图像
        tkinter.messagebox.showinfo('提示', '请选择要进行提取图片水印的图像')
        Fpath = filedialog.askopenfilename()

        if not Fpath:
            return

        # 打开图像
        img, _ = check_and_convert_image(Fpath)
        if img is None:
            return

        # 转换为numpy数组
        img_array = np.array(img)

        # 获取图像尺寸和通道数
        if len(img_array.shape) == 2:  # 灰度图像
            img_rows, img_cols = img_array.shape
            img_dims = 1
        else:  # 彩色图像
            img_rows, img_cols, img_dims = img_array.shape

        # 计算水印图像的尺寸（载体图像的1/2）
        mark_rows = img_rows // 2
        mark_cols = img_cols // 2

        print(f"隐写图像: {img_cols}x{img_rows}, 通道数: {img_dims}")
        print(f"提取的水印图像: {mark_cols}x{mark_rows}")

        # 创建水印图像数组
        if img_dims == 1:  # 灰度
            watermark_array = np.zeros((mark_rows, mark_cols), dtype=np.uint8)
        else:  # 彩色
            watermark_array = np.zeros((mark_rows, mark_cols, img_dims), dtype=np.uint8)

        # 从载体图像中提取水印信息
        for i in range(img_dims if img_dims > 1 else 1):  # 处理每个通道
            for j in range(mark_rows):
                for k in range(mark_cols):
                    # 计算载体图像中的位置
                    img_j = j * 2
                    img_k = k * 2

                    # 确保坐标在范围内
                    if img_j < img_rows and img_k < img_cols:
                        # 从载体图像中提取低4位，并左移4位恢复为高4位
                        if img_dims == 1:  # 灰度
                            extracted_bits = img_array[img_j, img_k] & 15  # 提取低4位
                        else:  # 彩色
                            extracted_bits = img_array[img_j, img_k, i] & 15  # 提取低4位

                        # 左移4位恢复为高4位
                        watermark_pixel = extracted_bits << 4

                        # 保存到水印图像
                        if img_dims == 1:
                            watermark_array[j, k] = watermark_pixel
                        else:
                            watermark_array[j, k, i] = watermark_pixel

        # 保存提取的水印
        watermark_img = Image.fromarray(watermark_array)

        # 选择保存位置
        tkinter.messagebox.showinfo('提示', '请选择将提取的水印保存的位置')
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="extracted_watermark_basic.png"
        )

        if save_path:
            watermark_img.save(save_path, 'PNG')
            tkinter.messagebox.showinfo('成功',
                                        f'基本水印提取完成！\n'
                                        f'水印尺寸: {mark_cols}x{mark_rows}\n'
                                        f'保存为: {save_path}')

            # 显示提取的水印
            plt.figure(figsize=(8, 6))
            plt.imshow(watermark_img)
            plt.title("提取的水印图像（基本版）")
            plt.axis('off')
            plt.tight_layout()
            plt.show()

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'基本水印提取失败:\n{str(e)}')
        print(f"详细错误: {e}")
        import traceback
        traceback.print_exc()


# ============ 改进的图像降级算法 ============
def Image_improved_yinxie():
    """改进的图像降级隐写"""
    try:
        # 选择载体图像
        tkinter.messagebox.showinfo('提示', '请选择载体图像')
        Fpath1 = filedialog.askopenfilename()

        if not Fpath1:
            return

        # 选择水印图像
        tkinter.messagebox.showinfo('提示', '请选择要隐写的水印图像')
        Fpath2 = filedialog.askopenfilename()

        if not Fpath2:
            return

        # 打开并检查图像
        img, _ = check_and_convert_image(Fpath1)
        mark, _ = check_and_convert_image(Fpath2)

        if img is None or mark is None:
            return

        # 转换为numpy数组
        img_array = np.array(img)
        mark_array = np.array(mark)

        # 检查尺寸 - 载体图像需要是水印图像的2倍
        mark_rows, mark_cols, mark_dims = mark_array.shape
        img_rows, img_cols, img_dims = img_array.shape

        # 检查载体图像是否足够大（至少是水印图像的2倍）
        if img_rows < mark_rows * 2 or img_cols < mark_cols * 2:
            tkinter.messagebox.showerror('错误',
                                         f'载体图像太小！\n'
                                         f'载体图像尺寸: {img_cols}x{img_rows}\n'
                                         f'水印图像需要载体尺寸至少为: {mark_cols * 2}x{mark_rows * 2}')
            return

        print(f"载体图像: {img_cols}x{img_rows}, 通道数: {img_dims}")
        print(f"水印图像: {mark_cols}x{mark_rows}, 通道数: {mark_dims}")

        # 清空载体图像的最低2位 (252 = 11111100)
        img_array = img_array & 252

        # 将水印图像的8位像素分成4个2位，分别嵌入到载体图像的2x2块中
        for i in range(min(mark_dims, img_dims)):  # 处理每个通道
            for j in range(mark_rows):
                for k in range(mark_cols):
                    # 获取水印像素值
                    if mark_dims == 1:  # 灰度图像
                        mark_pixel = mark_array[j, k]
                    else:  # 彩色图像
                        mark_pixel = mark_array[j, k, i]

                    # 将水印像素的8位分成4个2位
                    # 最高2位 (192 = 11000000)
                    bits1 = (mark_pixel & 192) >> 6
                    # 次高2位 (48 = 00110000)
                    bits2 = (mark_pixel & 48) >> 4
                    # 次低2位 (12 = 00001100)
                    bits3 = (mark_pixel & 12) >> 2
                    # 最低2位 (3 = 00000011)
                    bits4 = mark_pixel & 3

                    # 计算载体图像中的2x2块位置
                    img_j = j * 2
                    img_k = k * 2

                    # 确保坐标在范围内
                    if img_j + 1 < img_rows and img_k + 1 < img_cols:
                        # 将4个2位分别嵌入到2x2块的4个像素中
                        if img_dims == 1:  # 灰度载体
                            img_array[img_j, img_k] = img_array[img_j, img_k] + bits1
                            img_array[img_j, img_k + 1] = img_array[img_j, img_k + 1] + bits2
                            img_array[img_j + 1, img_k] = img_array[img_j + 1, img_k] + bits3
                            img_array[img_j + 1, img_k + 1] = img_array[img_j + 1, img_k + 1] + bits4
                        else:  # 彩色载体
                            img_array[img_j, img_k, i] = img_array[img_j, img_k, i] + bits1
                            img_array[img_j, img_k + 1, i] = img_array[img_j, img_k + 1, i] + bits2
                            img_array[img_j + 1, img_k, i] = img_array[img_j + 1, img_k, i] + bits3
                            img_array[img_j + 1, img_k + 1, i] = img_array[img_j + 1, img_k + 1, i] + bits4

        # 保存结果
        result_img = Image.fromarray(img_array)
        filename = os.path.basename(Fpath1)
        name_part = filename.rsplit('.', 1)[0]
        output_path = f"{name_part}_with_watermark_improved.png"

        result_img.save(output_path, 'PNG')
        tkinter.messagebox.showinfo('成功',
                                    f'改进的图像降级隐写完成！\n'
                                    f'载体图像: {img_cols}x{img_rows}\n'
                                    f'水印图像: {mark_cols}x{mark_rows}\n'
                                    f'保存为: {output_path}')

        # 显示对比
        show_image_comparison(Fpath1, output_path, "原始图像", "改进水印隐写后图像")

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'改进的图像降级隐写失败:\n{str(e)}')
        print(f"详细错误: {e}")
        import traceback
        traceback.print_exc()


def Image_improved_tiqu():
    """改进的图像降级提取"""
    try:
        # 选择隐写图像
        tkinter.messagebox.showinfo('提示', '请选择要进行提取图片水印的图像')
        Fpath = filedialog.askopenfilename()

        if not Fpath:
            return

        # 打开图像
        img, _ = check_and_convert_image(Fpath)
        if img is None:
            return

        # 转换为numpy数组
        img_array = np.array(img)

        # 获取图像尺寸和通道数
        if len(img_array.shape) == 2:  # 灰度图像
            img_rows, img_cols = img_array.shape
            img_dims = 1
        else:  # 彩色图像
            img_rows, img_cols, img_dims = img_array.shape

        # 计算水印图像的尺寸（载体图像的1/2）
        mark_rows = img_rows // 2
        mark_cols = img_cols // 2

        print(f"隐写图像: {img_cols}x{img_rows}, 通道数: {img_dims}")
        print(f"提取的水印图像: {mark_cols}x{mark_rows}")

        # 创建水印图像数组
        if img_dims == 1:  # 灰度
            watermark_array = np.zeros((mark_rows, mark_cols), dtype=np.uint8)
        else:  # 彩色
            watermark_array = np.zeros((mark_rows, mark_cols, img_dims), dtype=np.uint8)

        # 从载体图像的2x2块中提取水印信息
        for i in range(img_dims if img_dims > 1 else 1):  # 处理每个通道
            for j in range(mark_rows):
                for k in range(mark_cols):
                    # 计算载体图像中的2x2块位置
                    img_j = j * 2
                    img_k = k * 2

                    # 确保坐标在范围内
                    if img_j + 1 < img_rows and img_k + 1 < img_cols:
                        # 从2x2块的4个像素中提取最低2位
                        if img_dims == 1:  # 灰度
                            bits1 = img_array[img_j, img_k] & 3
                            bits2 = img_array[img_j, img_k + 1] & 3
                            bits3 = img_array[img_j + 1, img_k] & 3
                            bits4 = img_array[img_j + 1, img_k + 1] & 3
                        else:  # 彩色
                            bits1 = img_array[img_j, img_k, i] & 3
                            bits2 = img_array[img_j, img_k + 1, i] & 3
                            bits3 = img_array[img_j + 1, img_k, i] & 3
                            bits4 = img_array[img_j + 1, img_k + 1, i] & 3

                        # 将4个2位组合成一个8位像素
                        watermark_pixel = (bits1 << 6) | (bits2 << 4) | (bits3 << 2) | bits4

                        # 保存到水印图像
                        if img_dims == 1:
                            watermark_array[j, k] = watermark_pixel
                        else:
                            watermark_array[j, k, i] = watermark_pixel

        # 保存提取的水印
        watermark_img = Image.fromarray(watermark_array)

        # 选择保存位置
        tkinter.messagebox.showinfo('提示', '请选择将提取的水印保存的位置')
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="extracted_watermark_improved.png"
        )

        if save_path:
            watermark_img.save(save_path, 'PNG')
            tkinter.messagebox.showinfo('成功',
                                        f'改进水印提取完成！\n'
                                        f'水印尺寸: {mark_cols}x{mark_rows}\n'
                                        f'保存为: {save_path}')

            # 显示提取的水印
            plt.figure(figsize=(8, 6))
            plt.imshow(watermark_img)
            plt.title("提取的水印图像（改进版）")
            plt.axis('off')
            plt.tight_layout()
            plt.show()

    except Exception as e:
        tkinter.messagebox.showerror('错误', f'改进水印提取失败:\n{str(e)}')
        print(f"详细错误: {e}")
        import traceback
        traceback.print_exc()


# ============ GUI界面 ============
def create_basic_LSB():
    """基本LSB算法界面"""
    root = Toplevel()
    root.title("基本LSB算法")
    root.geometry('800x400')

    Label(root, text="基本LSB算法", font=fontStyle1).pack(pady=10)

    # 创建Frame容器
    left_frame = Frame(root)
    left_frame.place(x=30, y=60, width=340, height=300)

    right_frame = Frame(root)
    right_frame.place(x=430, y=60, width=340, height=300)

    # 左侧：嵌入功能
    Label(left_frame, text="隐写嵌入", font=fontStyle2).pack(pady=5)

    Button(left_frame, text="基本LSB算法水印嵌入",
           command=LSB_basic_yinxie, height=2, width=30).pack(pady=10)

    # 右侧：提取功能
    Label(right_frame, text="信息提取", font=fontStyle2).pack(pady=5)

    # 提取长度设置
    length_frame = Frame(right_frame)
    length_frame.pack(pady=5)
    Label(length_frame, text="提取长度:").pack(side=LEFT)
    length_entry = Entry(length_frame, width=10)
    length_entry.pack(side=LEFT, padx=5)
    length_entry.insert(0, str(LSB_basic_text_len))

    def set_extract_length():
        global LSB_basic_text_len
        try:
            LSB_basic_text_len = int(length_entry.get())
            tkinter.messagebox.showinfo('提示', f'提取信息长度设置为: {LSB_basic_text_len}')
        except:
            tkinter.messagebox.showerror('错误', '请输入有效的数字')

    Button(length_frame, text="设置", command=set_extract_length).pack(side=LEFT, padx=5)

    Button(right_frame, text="基本LSB算法水印提取",
           command=LSB_basic_tiqu, height=2, width=30).pack(pady=10)

    # 说明信息
    info_frame = Frame(root)
    info_frame.place(x=50, y=230, width=700, height=150)

    Label(info_frame, text="算法说明:", font=fontStyle2).pack(anchor=W)

    info_text1 = "∎ 基本LSB隐写：将信息嵌入到图像每个像素的最低有效位"
    info_text2 = "∎ 优点：实现简单，对图像质量影响小"
    info_text3 = "∎ 缺点：安全性较低，易被检测和攻击"
    info_text4 = "∎ 注意：JPG格式会自动转换为PNG，确保无损处理"

    Label(info_frame, text=info_text1, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text2, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text3, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text4, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)

    root.mainloop()


def create_random_interval():
    """LSB随机间隔法界面"""
    root = Toplevel()
    root.title("随机间隔法")
    root.geometry('800x400')

    Label(root, text="随机间隔法", font=fontStyle1).pack(pady=10)

    # 创建Frame容器
    left_frame = Frame(root)
    left_frame.place(x=30, y=60, width=340, height=300)

    right_frame = Frame(root)
    right_frame.place(x=430, y=60, width=340, height=300)

    # 左侧：嵌入功能
    Label(left_frame, text="隐写嵌入", font=fontStyle2).pack(pady=5)

    # 步长设置
    step_frame = Frame(left_frame)
    step_frame.pack(pady=5)
    Label(step_frame, text="步长:").pack(side=LEFT)
    step_entry = Entry(step_frame, width=10)
    step_entry.pack(side=LEFT, padx=5)
    step_entry.insert(0, str(LSB_suijijiange_step))

    def set_step():
        global LSB_suijijiange_step
        try:
            LSB_suijijiange_step = int(step_entry.get())
            tkinter.messagebox.showinfo('提示', f'随机间隔步长设置为: {LSB_suijijiange_step}')
        except:
            tkinter.messagebox.showerror('错误', '请输入有效的数字')

    Button(step_frame, text="设置", command=set_step).pack(side=LEFT, padx=5)

    Button(left_frame, text="LSB随机间隔法水印嵌入",
           command=LSB_suijijiange_yinxie, height=2, width=30).pack(pady=10)

    # 右侧：提取功能
    Label(right_frame, text="信息提取", font=fontStyle2).pack(pady=5)

    # 提取长度设置
    length_frame = Frame(right_frame)
    length_frame.pack(pady=5)
    Label(length_frame, text="提取长度:").pack(side=LEFT)
    length_entry = Entry(length_frame, width=10)
    length_entry.pack(side=LEFT, padx=5)
    length_entry.insert(0, str(LSB_suijijiange_text_len))

    def set_extract_length():
        global LSB_suijijiange_text_len
        try:
            LSB_suijijiange_text_len = int(length_entry.get())
            tkinter.messagebox.showinfo('提示', f'提取信息长度设置为: {LSB_suijijiange_text_len}')
        except:
            tkinter.messagebox.showerror('错误', '请输入有效的数字')

    Button(length_frame, text="设置", command=set_extract_length).pack(side=LEFT, padx=5)

    Button(right_frame, text="LSB随机间隔法水印提取",
           command=LSB_suijijiange_tiqu, height=2, width=30).pack(pady=10)

    # 说明信息
    info_frame = Frame(root)
    info_frame.place(x=50, y=230, width=700, height=150)

    Label(info_frame, text="算法说明:", font=fontStyle2).pack(anchor=W)

    info_text1 = "∎ 随机间隔法水印嵌入：选择图片和隐藏信息，进行随机间隔LSB隐写"
    info_text2 = "∎ 随机间隔法水印提取：选择隐写图片，使用相同随机种子提取信息"
    info_text3 = "∎ 优点：提高了安全性，隐写位置随机分布"
    info_text4 = "∎ 注意：JPG格式会自动转换为PNG，确保无损处理"

    Label(info_frame, text=info_text1, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text2, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text3, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text4, wraplength=650, justify=LEFT).pack(anchor=W, pady=2)

    root.mainloop()


def creatre_regional_verification():
    """区域校验位算法界面"""
    root = Toplevel()
    root.title("区域校验位算法")
    root.geometry('850x400')

    Label(root, text="区域校验位算法", font=fontStyle1).pack(pady=10)

    # 创建Frame容器
    left_frame = Frame(root)
    left_frame.place(x=30, y=60, width=370, height=300)

    right_frame = Frame(root)
    right_frame.place(x=430, y=60, width=370, height=300)

    # 左侧：嵌入功能
    Label(left_frame, text="隐写嵌入", font=fontStyle2).pack(pady=5)

    # 区域大小设置
    size_frame = Frame(left_frame)
    size_frame.pack(pady=5)
    Label(size_frame, text="区域大小:").pack(side=LEFT)
    size_entry = Entry(size_frame, width=10)
    size_entry.pack(side=LEFT, padx=5)
    size_entry.insert(0, str(LSB_quyujiaoyan_size))

    def set_region_size():
        global LSB_quyujiaoyan_size
        try:
            LSB_quyujiaoyan_size = int(size_entry.get())
            tkinter.messagebox.showinfo('提示', f'区域大小设置为: {LSB_quyujiaoyan_size}')
        except:
            tkinter.messagebox.showerror('错误', '请输入有效的数字')

    Button(size_frame, text="设置", command=set_region_size).pack(side=LEFT, padx=5)

    Button(left_frame, text="LSB区域校验位算法水印嵌入",
           command=LSB_quyujiaoyan_yinxie, height=2, width=35).pack(pady=10)

    # 右侧：提取功能
    Label(right_frame, text="信息提取", font=fontStyle2).pack(pady=5)

    # 提取长度设置
    length_frame = Frame(right_frame)
    length_frame.pack(pady=5)
    Label(length_frame, text="提取长度:").pack(side=LEFT)
    length_entry = Entry(length_frame, width=10)
    length_entry.pack(side=LEFT, padx=5)
    length_entry.insert(0, str(LSB_quyujiaoyan_text_len))

    def set_extract_length():
        global LSB_quyujiaoyan_text_len
        try:
            LSB_quyujiaoyan_text_len = int(length_entry.get())
            tkinter.messagebox.showinfo('提示', f'提取信息长度设置为: {LSB_quyujiaoyan_text_len}')
        except:
            tkinter.messagebox.showerror('错误', '请输入有效的数字')

    Button(length_frame, text="设置", command=set_extract_length).pack(side=LEFT, padx=5)

    Button(right_frame, text="LSB区域校验位算法水印提取",
           command=LSB_quyujiaoyan_tiqu, height=2, width=35).pack(pady=10)

    # 说明信息
    info_frame = Frame(root)
    info_frame.place(x=50, y=230, width=750, height=150)

    Label(info_frame, text="算法说明:", font=fontStyle2).pack(anchor=W)

    info_text1 = "∎ 区域校验位算法：将多个像素分为一组，通过校验位控制信息嵌入"
    info_text2 = "∎ 嵌入：计算区域像素LSB总和，调整单个像素使校验位匹配隐藏信息"
    info_text3 = "∎ 提取：计算区域LSB总和，取校验位作为提取的信息位"
    info_text4 = "∎ 优点：提高了鲁棒性和容错性"

    Label(info_frame, text=info_text1, wraplength=700, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text2, wraplength=700, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text3, wraplength=700, justify=LEFT).pack(anchor=W, pady=2)
    Label(info_frame, text=info_text4, wraplength=700, justify=LEFT).pack(anchor=W, pady=2)

    root.mainloop()


def create_image_downgrade():
    """图像降级算法界面（包含基本版和改进版）"""
    root = Toplevel()
    root.title("图像降级算法")
    root.geometry('900x400')

    Label(root, text="图像降级算法对比", font=fontStyle1).pack(pady=10)

    # 创建Frame容器
    basic_frame = Frame(root)
    basic_frame.place(x=50, y=60, width=380, height=200)

    improved_frame = Frame(root)
    improved_frame.place(x=470, y=60, width=380, height=200)

    # 基本版图像降级算法
    Label(basic_frame, text="基本图像降级算法", font=fontStyle2).pack(pady=5)

    embed_frame = Frame(basic_frame)
    embed_frame.pack(pady=5)
    Button(embed_frame, text="水印嵌入",
           command=Image_basic_yinxie, height=2, width=15).pack(side=LEFT, padx=5)
    Button(embed_frame, text="水印提取",
           command=Image_basic_tiqu, height=2, width=15).pack(side=LEFT, padx=5)

    # 基本版说明
    basic_info_frame = Frame(basic_frame)
    basic_info_frame.place(x=10, y=100, width=360, height=90)

    basic_info_text = "∎ 基本算法：将水印图像的高4位嵌入到载体图像的低4位"
    basic_info_text2 = "∎ 载体尺寸需为水印的2倍"
    basic_info_text3 = "∎ 适用于快速但要求不高的场景"

    Label(basic_info_frame, text=basic_info_text, wraplength=350, justify=LEFT).pack(anchor=W)
    Label(basic_info_frame, text=basic_info_text2, wraplength=350, justify=LEFT).pack(anchor=W)
    Label(basic_info_frame, text=basic_info_text3, wraplength=350, justify=LEFT).pack(anchor=W)

    # 改进版图像降级算法
    Label(improved_frame, text="改进图像降级算法", font=fontStyle2).pack(pady=5)

    improved_embed_frame = Frame(improved_frame)
    improved_embed_frame.pack(pady=5)
    Button(improved_embed_frame, text="水印嵌入",
           command=Image_improved_yinxie, height=2, width=15).pack(side=LEFT, padx=5)
    Button(improved_embed_frame, text="水印提取",
           command=Image_improved_tiqu, height=2, width=15).pack(side=LEFT, padx=5)

    # 改进版说明
    improved_info_frame = Frame(improved_frame)
    improved_info_frame.place(x=10, y=100, width=360, height=90)

    improved_info_text = "∎ 改进算法：将水印的8位分成4个2位，嵌入到2x2块中"
    improved_info_text2 = "∎ 载体尺寸需为水印的2倍"
    improved_info_text3 = "∎ 提高了水印质量和鲁棒性"

    Label(improved_info_frame, text=improved_info_text, wraplength=350, justify=LEFT).pack(anchor=W)
    Label(improved_info_frame, text=improved_info_text2, wraplength=350, justify=LEFT).pack(anchor=W)
    Label(improved_info_frame, text=improved_info_text3, wraplength=350, justify=LEFT).pack(anchor=W)

    root.mainloop()


def create_LSB_improve():
    """LSB算法改进主界面"""
    root = Toplevel()
    root.title("LSB算法对比")
    root.geometry('900x500')

    Label(root, text="LSB算法对比", font=fontStyle1).pack(pady=10)

    # 创建Frame容器
    button_frame = Frame(root)
    button_frame.place(x=50, y=80, width=800, height=250)

    # 第一行：基本LSB算法
    basic_frame = Frame(button_frame)
    basic_frame.place(x=0, y=0, width=800, height=80)
    Label(basic_frame, text="基本LSB算法", font=fontStyle2).place(x=10, y=10)
    Button(basic_frame, text="基本LSB隐写与提取",
           command=create_basic_LSB, height=2, width=25).place(x=150, y=5)

    basic_info = "∎ 基本LSB：简单直接，将信息嵌入到每个像素的最低有效位"
    basic_info2 = "∎ 优点：实现简单，对图像质量影响小；缺点：安全性较低"
    Label(basic_frame, text=basic_info, wraplength=600, justify=LEFT).place(x=350, y=10)
    Label(basic_frame, text=basic_info2, wraplength=600, justify=LEFT).place(x=350, y=35)

    # 第二行：随机间隔法
    random_frame = Frame(button_frame)
    random_frame.place(x=0, y=90, width=800, height=80)
    Label(random_frame, text="随机间隔法", font=fontStyle2).place(x=10, y=10)
    Button(random_frame, text="随机间隔法隐写与提取",
           command=create_random_interval, height=2, width=25).place(x=150, y=5)

    random_info = "∎ 随机间隔法：在LSB基础上，使用随机间隔选取像素位置"
    random_info2 = "∎ 优点：提高了安全性；缺点：需要固定随机种子"
    Label(random_frame, text=random_info, wraplength=600, justify=LEFT).place(x=350, y=10)
    Label(random_frame, text=random_info2, wraplength=600, justify=LEFT).place(x=350, y=35)

    # 第三行：区域校验位算法
    region_frame = Frame(button_frame)
    region_frame.place(x=0, y=180, width=800, height=80)
    Label(region_frame, text="区域校验位算法", font=fontStyle2).place(x=10, y=10)
    Button(region_frame, text="区域校验位法隐写与提取",
           command=creatre_regional_verification, height=2, width=25).place(x=150, y=5)

    region_info = "∎ 区域校验位法：将多个像素分为一组，通过校验位控制信息嵌入"
    region_info2 = "∎ 优点：提高了鲁棒性和容错性；缺点：实现较复杂"
    Label(region_frame, text=region_info, wraplength=600, justify=LEFT).place(x=350, y=10)
    Label(region_frame, text=region_info2, wraplength=600, justify=LEFT).place(x=350, y=35)

    # 对比说明
    compare_frame = Frame(root)
    compare_frame.place(x=50, y=350, width=800, height=120)

    Label(compare_frame, text="算法对比总结:", font=fontStyle2).pack(anchor=W, pady=5)

    compare_text = "∎ 基本LSB：最简单，适合初学者理解和快速实现，但安全性最低"
    compare_text2 = "∎ 随机间隔法：提高了安全性，隐写位置随机，不易被检测"
    compare_text3 = "∎ 区域校验位法：鲁棒性最好，适合对容错性要求高的场景"
    compare_text4 = "∎ 建议：根据需求选择合适的算法进行对比实验"

    Label(compare_frame, text=compare_text, wraplength=780, justify=LEFT).pack(anchor=W)
    Label(compare_frame, text=compare_text2, wraplength=780, justify=LEFT).pack(anchor=W)
    Label(compare_frame, text=compare_text3, wraplength=780, justify=LEFT).pack(anchor=W)
    Label(compare_frame, text=compare_text4, wraplength=780, justify=LEFT).pack(anchor=W)

    root.mainloop()


# ============ 主程序 ============
def main():
    """主程序"""
    root = Tk()
    root.title("图像隐写系统 - LSB对比与图像降级对比")
    root.geometry('900x550')

    # 设置字体
    global fontStyle, fontStyle1, fontStyle2
    fontStyle = tkFont.Font(family="Microsoft YaHei", size=20)
    fontStyle1 = tkFont.Font(family="Microsoft YaHei", size=15)
    fontStyle2 = tkFont.Font(family="Microsoft YaHei", size=10)

    # 标题
    Label(root, text="图像隐写对比系统", font=fontStyle).pack(pady=20)
    Label(root, text="LSB算法对比与图像降级算法对比", font=fontStyle1).pack(pady=10)

    # 功能按钮
    button_frame = Frame(root)
    button_frame.pack(pady=50)

    Button(button_frame, text='LSB算法对比',
           command=create_LSB_improve, height=3, width=20,
           font=fontStyle1).pack(side=LEFT, padx=20)

    Button(button_frame, text='图像降级对比',
           command=create_image_downgrade, height=3, width=20,
           font=fontStyle1).pack(side=LEFT, padx=20)

    # 说明信息
    info_frame = Frame(root)
    info_frame.pack(pady=30)

    info_label1 = Label(info_frame,
                        text="LSB算法对比包含：\n"
                             "    1. 基本LSB算法 - 基础对比\n"
                             "    2. 随机间隔法 - 安全性对比\n"
                             "    3. 区域校验位算法 - 鲁棒性对比",
                        font=fontStyle2, justify=LEFT)
    info_label1.pack(side=LEFT, padx=20)

    info_label2 = Label(info_frame,
                        text="图像降级对比包含：\n"
                             "    1. 基本图像降级算法 - 基础版\n"
                             "    2. 改进图像降级算法 - 优化版\n"
                             "    3. 两种算法的效果对比",
                        font=fontStyle2, justify=LEFT)
    info_label2.pack(side=LEFT, padx=20)

    # 注意事项
    notice_frame = Frame(root)
    notice_frame.pack(pady=20)

    notice_text = "注意事项：\n" \
                  "1. 支持JPG、PNG、BMP等多种格式，JPG会自动转换为PNG处理\n" \
                  "2. 建议使用PNG或BMP格式以获得最佳效果\n" \
                  "3. 提取时需要正确设置参数（步长、区域大小、提取长度）\n" \
                  "4. 本系统专为算法对比实验设计，请记录不同算法的效果差异"

    Label(notice_frame, text=notice_text, font=fontStyle2,
          justify=LEFT, fg='red').pack()

    root.mainloop()


if __name__ == "__main__":
    main()