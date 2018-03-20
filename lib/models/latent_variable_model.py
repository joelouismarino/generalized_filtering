import torch.nn as nn


class LatentVariableModel(nn.Module):
    """
    Abstract class for a (dynamical) latent variable model (DLVM). All models
    inherit from this class.
    """
    def __init__(model_config):
        super(LatentVariableModel, self).__init__()

    def _construct(self, model_config):
        """
        Abstract method for constructing a dynamical latent variable model using
        the model configuration file.

        Args:
            model_config (dict): dictionary containing model configuration params
        """
        raise NotImplementedError

    def infer(self, observation):
        """
        Abstract method for perfoming inference of the approximate posterior
        over the latent variables.

        Args:
            observation (tensor): observation to infer latent variables from
        """
        raise NotImplementedError

    def generate(self, gen=False, n_samples=1):
        """
        Abstract method for generating observations, i.e. running the generative
        model forward.

        Args:
            gen (boolean): whether to sample from prior or approximate posterior
            n_samples (int): number of samples to draw and evaluate
        """
        raise NotImplementedError

    def step(self):
        """
        Abstract method for stepping the generative model forward one step in
        the sequence.
        """
        raise NotImplementedError

    def re_init(self):
        """
        Abstract method for reinitializing the state (approximate posterior and
        priors) of the dynamical latent variable model.
        """
        raise NotImplementedError

    def kl_divergences(self, averaged=False):
        """
        Estimate the KL divergence (at each latent level).

        Args:
            averaged (boolean): whether to average over the batch dimension
        """
        # TODO: keep this general across conv, fc
        kl = []
        for latent_level in self.levels:
            kl.append(latent_level.latent.kl_divergence(analytical=False).sum(4).sum(3).sum(2).mean(1))
        if averaged:
            [level_kl.mean(dim=0) for level_kl in kl]
        else:
            return kl

    def conditional_log_likelihoods(self, observation, averaged=False):
        """
        Estimate the conditional log-likelihood.

        Args:
            observation (tensor): observation to evaluate
            averaged (boolean): whether to average over the batch dimension
        """
        # TODO: keep this general across conv, fc
        if len(input.data.shape) == 4:
            observation = observation.unsqueeze(1) # add sample dimension
        log_prob = self.output_dist.log_prob(sample=observation).sub_(np.log(256.))
        log_prob = log_prob.sum(4).sum(3).sum(2).mean(1)
        if averaged:
            log_prob = log_prob.mean(dim=0)
        return log_prob

    def free_energy(self, observation, averaged=False):
        """
        Estimate the free energy.

        Args:
            observation (tensor): observation to evaluate
            averaged (boolean): whether to average over the batch dimension
        """
        cond_log_like = self.conditional_log_likelihoods(observation)
        kl = sum(self.kl_divergences())
        lower_bound = cond_log_like - kl
        if averaged:
            return lower_bound.mean(dim=0)
        else:
            return lower_bound

    def losses(self, observation, averaged=False):
        """
        Estimate all losses.

        Args:
            observation (tensor): observation to evaluate
            averaged (boolean): whether to average over the batch dimension
        """
        cond_log_like = self.conditional_log_likelihoods(observation)
        kl = self.kl_divergences()
        lower_bound = cond_log_like - sum(kl)
        if averaged:
            return lower_bound.mean(dim=0), cond_log_like.mean(dim=0), [level_kl.mean(dim=0) for level_kl in kl]
        else:
            return lower_bound, cond_log_like, kl

    def inference_parameters(self):
        """
        Abstract method for obtaining the inference parameters.
        """
        raise NotImplementedError

    def generative_parameters(self):
        """
        Abstract method for obtaining the generative parameters.
        """
        raise NotImplementedError