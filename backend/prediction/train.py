import argparse
import os
import numpy as np
from datetime import datetime

import torchvision.transforms as transforms
from torchvision.utils import save_image

from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable
from torch.utils.tensorboard import SummaryWriter

import torch.nn as nn
import torch.nn.functional as F
import torch

from datasets import LotteryDataset
from LotoNet import LotoNet

# tensorboard --logdir F:\repositories\misc\tensorboard-logs\prediction_num\
# python .\prediction\train.py --lottery_type loto7 --n_epochs 10
# python .\prediction\train.py --lottery_type miniloto --n_epochs 100
# python .\prediction\train.py --lottery_type numbers3 --n_epochs 100

parser = argparse.ArgumentParser()
parser.add_argument("--n_epochs", type=int, default=50, help="number of epochs of training")
parser.add_argument("--batch_size", type=int, default=10, help="size of the batches")
parser.add_argument("--batch_size_val", type=int, default=10, help="size of the batches")
parser.add_argument("--lr", type=float, default=0.001, help="adam: learning rate")
parser.add_argument("--lottery_type", type=str, default='loto7', help="lottery type to train")
parser.add_argument("--n_cpu", type=int, default=8, help="number of cpu threads to use during batch generation")
# parser.add_argument("--latent_dim", type=int, default=100, help="dimensionality of the latent space")
# parser.add_argument("--img_size", type=int, default=28, help="size of each image dimension")
# parser.add_argument("--channels", type=int, default=1, help="number of image channels")
parser.add_argument("--logs_dir", type=str, default='F:/repositories/misc/tensorboard-logs/prediction_num', help="logs dir")

opt = parser.parse_args()
print(opt)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main(): 
    train_transforms = transforms.Compose([
        #transforms.RandomResizedCrop(IMG_SIZE),
        #transforms.RandomHorizontalFlip(),
        #transforms.RandomVerticalFlip(),
        #transforms.RandomRotation(30),
        #transforms.ToTensor()
        #transforms.Normalize(IMG_MEAN, IMG_STD)
    ])

    val_transforms = transforms.Compose([
        #transforms.Resize(IMG_SIZE),
        #transforms.ToTensor()
        #transforms.Normalize(IMG_MEAN, IMG_STD)
    ])

    path = 'E:/datasets/loto/'
    train_dataset = LotteryDataset(root=os.path.join(path, "train"), lottery_type=opt.lottery_type, transform=train_transforms)
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=opt.batch_size, shuffle=True)

    val_dataset = LotteryDataset(root=os.path.join(path, "val"), lottery_type=opt.lottery_type, transform=train_transforms)
    val_loader = torch.utils.data.DataLoader(dataset=val_dataset, batch_size=opt.batch_size_val, shuffle=False)

    offset = 0 if val_dataset.lottery_type == 'numbers3' or val_dataset.lottery_type == 'numbers4' else 1

    learning_rate = opt.lr
    
    def weights_init(m):
        if isinstance(m, nn.Conv2d):
            nn.init.xavier_uniform_(m.weight.data)
            if m.bias is not None:
                m.bias.data.zero_()

    model = LotoNet().to(device)
    #model.apply(weights_init)

    total_step = len(train_loader)
    criterion = nn.BCEWithLogitsLoss()

    # 只有放入到optimizer中，和requires_grad为true的参数才会被更新
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # ----------
    #  Training
    # ----------
    for epoch in range(opt.n_epochs):

        # loss_value = runner.train(model, criterion, optimizer, device, train_loader, epoch)
        model.train()
        for index, (x, y) in enumerate(train_loader):

            x = x.to(device)
            y = y.to(device)

            optimizer.zero_grad()
            y_hat = model(x)
            loss = criterion(y_hat, y)
            loss.backward()

            # 更新参数
            optimizer.step()
        
        loss_value = loss.item()
        # draw_chart(loss_value, epoch + 1, opt.logs_dir)

        print('Epoch: {}, Loss: {:e}'.format(epoch + 1, loss_value))
            
        if (epoch + 1) % 5 == 0: 
            
            # test_loss, correct = runner.val(model, criterion, optimizer, device, val_loader)
            model.eval()
            test_loss = 0
            correct = 0
            with torch.no_grad():
                
                for index, (x, y) in enumerate(val_loader):          

                    x=x.to(device)
                    y=y.to(device)

                    #optimizer.zero_grad()

                    y_hat = model(x)
                    test_loss += criterion(y_hat, y).item() # sum up batch loss

                    pred_num = val_dataset.bin_to_numbers(y_hat.cpu())
                    num = val_dataset.bin_to_numbers(y.cpu())

                    # print('y_hat: ', y_hat)
                    print('---------------------- pred_num ----------------------')
                    print(pred_num + offset)
                    # print(np.unique((pred_num + 1).ravel()))
                    print('---------------------- num ---------------------------')
                    print(num + offset)
                    # print(np.unique((num + 1).ravel()))

                    correct += (pred_num == num).sum()

            test_loss /= len(val_loader.dataset)
            total = len(val_dataset) * val_dataset.num_total
            score = correct / total
            print('---------------------- val loss {:.2f} -------------------'.format(test_loss))
            print('---------------------- accuracy: {}/{}({:.1f}%) -----------'.format(correct, total, 100. * score))

    checkpoint_filename = "checkpoint_epoch({})_{}_{}.pth".format(opt.n_epochs, val_dataset.lottery_type, datetime.now().strftime("%Y_%m_%d_%H%M"))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    torch.save(model.state_dict(), os.path.join(dir_path, 'checkpoint', checkpoint_filename))
    print(" checkpoint file {} saved.".format(checkpoint_filename))


def draw_chart(loss_value, epoch, logs_dir):

    logs_dir = os.path.join(logs_dir, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

    with SummaryWriter(log_dir=logs_dir, flush_secs=2, comment='train') as writer:
        
        writer.add_histogram('his/loss', loss_value, epoch)
        writer.add_scalar('data/loss', loss_value, epoch)

        #writer.add_histogram('his/y', y, epoch)
        #writer.add_scalar('data/y', y, epoch)
        #writer.add_scalar('data/loss', loss, epoch)
        #writer.add_scalars('data/data_group', {'x': x, 'y': y}, epoch)

if __name__ == '__main__':
    main()