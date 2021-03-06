import time
from pathlib import Path
import comet_ml
import sys
import copy
import os
import torch
from models.SonderVITON import SonderFlowEstimator
from utils import load_opts, Timer, set_mode
from data.dataloader import get_loader
from addict import Dict

COMET_API_KEY = "XDFR9dUZZYkdwlgAEUZwhSssr"
project_name="VirtualTryon"
workspace="abc123yuanrui"
comet_exp = comet_ml.Experiment(COMET_API_KEY, project_name, workspace)
# from data import CreateDataLoader
# from models import create_model
# from util.visualizer import Visualizer

if __name__ == "__main__":
    root = Path(__file__).parent.resolve()
    opt_file = "shared/defaults.yml"

    opt = load_opts(path=root / opt_file)

    # Set up comet experiment:
#     comet_exp = Experiment(workspace=opt.comet.workspace, project_name=opt.comet.project_name)
    if comet_exp is not None:
        comet_exp.log_asset(file_data=str(root / opt_file), file_name=root / opt_file)
        comet_exp.log_parameters(opt)

    opt.comet.exp = comet_exp

    opt = set_mode("train", opt)
    val_loader = get_loader(opt)
    test_display_images = [iter(val_loader).next() for i in range(opt.comet.display_size)]

    opt = set_mode("train", opt)
    loader = get_loader(opt)
    train_display_images = [iter(loader).next() for i in range(opt.comet.display_size)]

    model = SonderFlowEstimator()
    model.initialize(opt)
    model.setup()

    total_steps = 0
    
    save_path = "/checkpoints-clothflow"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for epoch in range(opt.train.epochs):
        epoch_start_time = time.time()
        iter_data_time = time.time()
        epoch_iter = 0

        for i, data in enumerate(loader):

            with Timer("Elapsed time in update " + str(i) + ": %f"):

                total_steps += opt.data.loaders.batch_size
                epoch_iter += opt.data.loaders.batch_size
                model.set_input(Dict(data))
                model.optimize_parameters()

                if total_steps % opt.val.save_im_freq == 0:
                    model.save_test_images(test_display_images, total_steps)
    
        if epoch % 4 == 0:
            model.save_checkpoints(epoch, save_path)
            print("checkpoint saved!, epoch:", epoch)
            
    model.save_checkpoints(self, epoch, save_path)
    model.cuda()