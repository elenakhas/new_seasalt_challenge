"""Demo PyTorch MNIST model for the Seasalt.ai technical challenge."""


import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms


class Net(nn.Module):
    '''The definition of the network'''

    def __init__(self):
        '''Initialize the network'''
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4*4*50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x):
        '''Define the forward layer'''
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def train(model, device, loader, optimizer, epoch, min_train=False):
    '''Train the model'''
    model.train()
    for idx, (data, target) in enumerate(loader):
        if min_train:
            if idx >= len(loader)*0.1:
                break
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if idx % 5 == 0:
            print('Train epoch {} ({:.0f}%)\t Loss: {:.6f}'.format(
                epoch, 100. * idx / len(train_loader), loss.item()))


def test(model, device, loader, optimizer, epoch):
    '''Test the model'''
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
    test_loss /= len(loader.dataset)
    print('Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'.format(
        test_loss, correct, len(loader.dataset),
        100. * correct/len(loader.dataset)))


train_loader = torch.utils.data.DataLoader(
        datasets.MNIST(root='./input',
                       train=True,
                       download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor()])),
        batch_size=16, shuffle=True)


test_loader = torch.utils.data.DataLoader(
        datasets.MNIST('./input',
                       train=False,
                       download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor()])),
        batch_size=16, shuffle=True)

model = Net().to(torch.device("cpu"))

optimizer = optim.SGD(model.parameters(), lr=0.01)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min_train",
                        help="Train on 10% of train set",
                        required=False, action='store_true')
    args = parser.parse_args()

    for epoch in range(1, 2):
        train(model, torch.device("cpu"), train_loader,
              optimizer, epoch, args.min_train)

    test(model, torch.device("cpu"), test_loader, optimizer, epoch)

    torch.save(model.state_dict(), 'mnist_model.pth')
