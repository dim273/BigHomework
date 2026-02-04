import os
import sys
sys.path.append('.')
from utils import create_train_val_test_split, check_dataset_structure

def main():
    data_dir = '../data/Animals-10'
    output_dir = '../data'
    
    # 检查数据集结构
    check_dataset_structure(data_dir)
    
    # 创建数据集划分
    print("\nCreating dataset split...")
    create_train_val_test_split(data_dir, output_dir)
    
    # 可视化样本图像
    from utils import visualize_sample_images
    visualize_sample_images(data_dir, f'{output_dir}/train.csv', save_path='../results/sample_images.png')
    
    print("\nData preparation completed!")

if __name__ == '__main__':
    main()