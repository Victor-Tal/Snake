#---------------------------------------
#Cordero Correa Victor Hugo
#----------------------------------------

#--------------------------------------------------
#Importamos la librerias correspondientes
#---------------------------------------------------
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


#--------------------------------------------------------------------------------------
#Definimos la clase Linear_QNet para el tamaño de la entrada y salida
#---------------------------------------------------------------------------------------
class Linear_QNet(nn.Module):
  #self, tamaño_de_entrada, tamaño_oculto, tamaño_de_salida
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        #------------------------------------------------
        #nn.Linear(tamaño_de_entrada, tamaño_oculto) 
        #nn.Linear(tamaño_oculto, tamaño_de_salida)
        #-------------------------------------------------
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
  #-----------------------------------------------------------
  #Definimos como es que se hara para ir para adelante
  #------------------------------------------------------------
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
 #------------------------------------------------------------------------------------
 #Definimos que se guarde para que pueda guardar los datos y pueda ir aprendiendo
 #-------------------------------------------------------------------------------------
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
      #ruta_carpeta_modelo, nombre_archivo)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


#-------------------------------------------
#Definimos la clase para QTrainer
#-------------------------------------------
class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

#---------------------------------------------------------------------
#
#---------------------------------------------------------------------

    def train_step(self, state, action, reward, next_state, done):
      #train_step(yo, estado, acción, recompensa, siguiente_estado, hecho
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        #------------------------------------------------------
        # 1: Valores de Q pronosticados con el estado actual
        #-------------------------------------------------------
        pred = self.model(state)

        target = pred.clone()        
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new

        #------------------------------------------------------------------------------------------------
        # 2: Q_new = r + y * max(next_predicted Q value) -> solo haz esto si no lo haces
         # pred.clon()
         # preds[argmax(acción)] = Q_nuevo
         #------------------------------------------------------------------------------------------------
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()

#Termina model.py