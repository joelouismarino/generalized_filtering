import torch.optim as opt
from torch.optim.lr_scheduler import ExponentialLR


def load_opt_sched(train_config, model):

    inf_params = model.inference_parameters()
    gen_params = model.generative_parameters()

    opt_name = train_config['optimizer'].lower().replace('_', '').strip()
    if opt_name == 'sgd':
        optimizer = opt.SGD
    elif opt_name == 'rmsprop':
        optimizer = opt.RMSprop
    elif opt_name == 'adam':
        optimizer = opt.Adam

    inf_opt = optimizer(inf_params, lr=train_config['encoder_learning_rate'])
    gen_opt = optimizer(gen_params, lr=train_config['decoder_learning_rate'])

    inf_sched = ExponentialLR(enc_opt, 0.999)
    gen_sched = ExponentialLR(dec_opt, 0.999)

    return (inf_opt, gen_opt), (inf_sched, gen_sched)