import os
import numpy as np
import pandas as pd
from torch.utils.data import Dataset

class LotteryDataset(Dataset):

    def __init__(self, root, lottery_type, transform=None):

        self.lottery_type = lottery_type

        self.num_start = {'loto7': 2, 'loto6': 2, 'miniloto': 2, 'numbers3': 2, 'numbers4': 2}
        self.num_end = {'loto7': 9, 'loto6': 8, 'miniloto': 7, 'numbers3': 5, 'numbers4': 6}
        self.num_total = self.num_end[self.lottery_type] - self.num_start[self.lottery_type]

        self.result_bit = {'loto7': 37, 'loto6': 43, 'miniloto': 31, 'numbers3': 30, 'numbers4': 40}

        self.transform = transform

        # 每次输出的数据高度和数据宽度一致，同为64位
        self.height = 64

        if root is not None:
            
            self.csv_file = os.path.join(root, self.lottery_type + '.csv')
            # csv_file = os.path.join('E:/datasets/loto/train/', 'loto7.csv')
            # 读入全部数据并按回数排序
            df = pd.read_csv(self.csv_file, header=None).sort_values(by=[1])

            # 数据结构为 二进制年月日(yymmdd)20位，二进制抽选数字44位合计64位，数据为0和1
            # 每回的输出数据为64*64的ndarray
            self.complete_data = self.dataframe_to_bin(df)

    def __len__(self):
        return len(self.complete_data) - self.height

    def __getitem__(self, idx):
        
        history = self.complete_data[idx: idx + 64]
        history = np.expand_dims(history, 0)

        result = self.complete_data[idx + 64][20:]

        if self.transform:
            history = self.transform(history)

        return history, result

    # 转换dataframe格式数据为2进制datasets
    # dataframe列为
    # lottery_date	times	number1	number2	number3	number4	number5	number6	number7	bonus_1	bonus_2 ...
    def dataframe_to_bin(self, df):

        # 取得数据中的日期(第一列)
        array_date = df.iloc[:, 0].apply(lambda x: bin(int(x[2:].replace('-', '').replace('/', '')))[2:].zfill(20)).apply(lambda x: list(x))
        array_date = np.stack(array_date.to_numpy(), axis=0).astype('float32')

        # 取得数据中的数字部分
        offset = 0 if self.lottery_type == 'numbers3' or self.lottery_type == 'numbers4' else 1
        df_numbers = df.iloc[:, self.num_start[self.lottery_type]: self.num_end[self.lottery_type]].to_numpy() - offset
        array_numbers = np.zeros([df_numbers.shape[0], 44], dtype='float32')
        for i, row in enumerate(df_numbers):
            
            if self.lottery_type == 'numbers3':
                row[1] += 10; row[2] += 20
            if self.lottery_type == 'numbers4':
                row[1] += 10; row[2] += 20; row[3] += 30

            array_numbers[i][row] = 1

        # 数据结构为 二进制年月日(yymmdd)20位，二进制抽选数字44位合计64位，数据为0和1
        # 每回的输出数据为64*64的ndarray
        return np.concatenate((array_date, array_numbers), axis=1)


    # 转变result格式的44位数据为数字
    # 输入(batchsize, 44)，输出抽选结果数字，loto7时为[2, 3, 12, 21, 24, 29, 36]
    # loto7 范围为1-37
    # loto6 范围为1-43
    # miniloto 范围为1-31
    # numbers3 范围为3个1-10，共30
    # numbers4 范围为4个1-10，共40
    def bin_to_numbers(self, num_in_bin, top_count=None):
        
        if not top_count or  top_count < self.num_total:
            top_count = self.num_total

        bit = self.result_bit[self.lottery_type]

        if type(num_in_bin).__module__ != np.__name__:
            num_in_bin = num_in_bin.numpy().copy()
        
        if self.lottery_type in ('numbers3', 'numbers4'):
            top_count_axis = top_count // self.num_total
            num_in_bin = num_in_bin[:, :self.num_total * 10].reshape(num_in_bin.shape[0], self.num_total, 10)
            result = np.argpartition(-num_in_bin, top_count_axis, axis=2)[:, :, :top_count_axis].reshape(num_in_bin.shape[0], top_count)
        else:
            num_in_bin = num_in_bin[:, :bit]
            result = np.argpartition(-num_in_bin, top_count, axis=1)[:, :top_count]
            result.sort(axis=1)

        return result

    # 转变数字数据格式为2进制datasets
    # 输入为类LotteryData的方法get_lottery_list的返回数据
    # 返回shape为[1, 64, 64]的2进制datasets
    # def numbers_to_bin(self, num_in_bin):



