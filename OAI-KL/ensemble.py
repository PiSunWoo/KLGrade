import pandas as pd
import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from dataset import ImageDataset

test = pd.read_csv('./KneeXray/Test_correct.csv') # _cn _clahe 등, 수정 O, 수정 x -> 결과 비교

transform = transforms.Compose([
                                transforms.ToTensor(),
                                transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5]),
                               ])

test_data = ImageDataset(test, transforms=transform)
testloader = DataLoader(test_data, batch_size=1, shuffle=False)

model_path = './models/'
submission_path = './submission/'
model_list = os.listdir(model_path)
model_list_pt = [file for file in model_list if file.endswith(".pt")]

for i in model_list_pt: 
    globals()['softmax_numpy_{}'.format(i)] = []
    model_ft = torch.load('{}{}'.format(model_path, i))

    for batch in testloader:
        with torch.no_grad():
            image = batch['image'].cuda()
            output = model_ft(image)
            softmax = nn.Softmax(dim=1)
            softmax_output = softmax(output).detach().cpu().numpy()
            globals()['softmax_numpy_{}'.format(i)].append(softmax_output)
            
preds = []
ensemble = [0 for i in range(1656)]
for i in range(1656):
    ensemble[i] = (globals()['softmax_numpy_{}'.format('kfold_CNN_2fold_epoch7.pt')][i] + globals()['softmax_numpy_{}'.format('kfold_CNN_5fold_epoch21.pt')][i]) / 2
    
    output = torch.tensor(ensemble[i])
    preds.extend([i.item() for i in torch.argmax(output, axis=1)])
    
submit = pd.DataFrame({'data':[i.split('/')[-1] for i in test['data']], 'label':preds})

submit.to_csv('{}ensemble_submission.csv'.format(submission_path), index=False)
print('save ensemble_submission.csv')