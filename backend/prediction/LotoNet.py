import torch.nn as nn
import torch.nn.functional as F
import torch

# Convolutional neural network LotoNet for loto numbers prediction
# output 44 numbers in 0,1 to describe loto numbers
class LotoNet(nn.Module):
    def __init__(self, num_classes=44):

        super().__init__()

        # input N, C1, W64, H64
        # output N, C64, W30, H30
        # self.original_feature_layer = nn.Sequential(
        #     nn.Conv2d(1, 64, kernel_size=5, stride=1),
        #     nn.BatchNorm2d(64),
        #     nn.ReLU(),
        #     nn.MaxPool2d(kernel_size=2, stride=2)
        #     )

        # input N, C1, W64, H64
        # output N, C64, W31, H31
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, stride=1),
            nn.MaxPool2d(kernel_size=2, stride=2)
            )

        # input N, C64, W31, H31
        # output N, C64, W14, H14
        self.layer2 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.MaxPool2d(kernel_size=2, stride=2)
            )

        # input N, C64, W14, H14
        # output N, num_classes
        self.fc = nn.Sequential(nn.Flatten(), 
            nn.Linear(64 * 14 * 14, 256),
            nn.Linear(256, num_classes))
        
    def forward(self, x):
        
        out = self.layer1(x)
        out = self.layer2(out)

        #branch1 = self.original_feature_layer(x)
        #branch2 = self.con1x1_layer(x)
        #branch3 = self.con3x3_layer(x)

        #out += branch1
        out = self.fc(out)

        return out