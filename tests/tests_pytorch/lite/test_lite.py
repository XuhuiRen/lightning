from re import escape

import pytest

from lightning_fabric.accelerators import CPUAccelerator as LiteCPUAccelerator
from lightning_fabric.plugins import DoublePrecision as LiteDoublePrecision
from lightning_fabric.plugins import Precision as LitePrecision
from lightning_fabric.plugins.environments import SLURMEnvironment
from lightning_fabric.strategies import DDPStrategy as LiteDDPStrategy
from lightning_fabric.strategies import DeepSpeedStrategy as LiteDeepSpeedStrategy
from lightning_fabric.strategies import SingleDeviceStrategy as LiteSingleDeviceStrategy
from pytorch_lightning.accelerators import CUDAAccelerator as PLCUDAAccelerator
from pytorch_lightning.lite import LightningLite
from pytorch_lightning.plugins import DoublePrecisionPlugin as PLDoublePrecisionPlugin
from pytorch_lightning.plugins import PrecisionPlugin as PLPrecisionPlugin
from pytorch_lightning.strategies import DDPStrategy as PLDDPStrategy
from pytorch_lightning.strategies import DeepSpeedStrategy as PLDeepSpeedStrategy
from tests_pytorch.helpers.runif import RunIf


class EmptyLite(LightningLite):
    def run(self):
        pass


def test_lite_convert_pl_plugins(cuda_count_2):
    """Tests a few examples of passing PL-accelerators/strategies/plugins to the soon deprecated PL version of
    Lightning Lite for backward compatibility.

    Not all possible combinations of input arguments are tested.
    """

    # defaults
    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"):
        lite = EmptyLite()
    assert isinstance(lite._accelerator, LiteCPUAccelerator)
    assert isinstance(lite._precision, LitePrecision)
    assert isinstance(lite._strategy, LiteSingleDeviceStrategy)

    # accelerator and strategy passed separately
    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"):
        lite = EmptyLite(accelerator=PLCUDAAccelerator(), strategy=PLDDPStrategy())
    assert isinstance(lite._accelerator, PLCUDAAccelerator)
    assert isinstance(lite._precision, LitePrecision)
    assert isinstance(lite._strategy, LiteDDPStrategy)

    # accelerator passed to strategy
    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"):
        lite = EmptyLite(strategy=PLDDPStrategy(accelerator=PLCUDAAccelerator()))
    assert isinstance(lite._accelerator, PLCUDAAccelerator)
    assert isinstance(lite._strategy, LiteDDPStrategy)

    # kwargs passed to strategy
    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"):
        lite = EmptyLite(strategy=PLDDPStrategy(find_unused_parameters=False))
    assert isinstance(lite._strategy, LiteDDPStrategy)
    assert lite._strategy._ddp_kwargs == dict(find_unused_parameters=False)

    # plugins = instance
    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"):
        lite = EmptyLite(plugins=PLDoublePrecisionPlugin())
    assert isinstance(lite._precision, LiteDoublePrecision)

    # plugins = list
    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"):
        lite = EmptyLite(plugins=[PLDoublePrecisionPlugin(), SLURMEnvironment()], devices=2)
    assert isinstance(lite._precision, LiteDoublePrecision)
    assert isinstance(lite._strategy.cluster_environment, SLURMEnvironment)


def test_lite_convert_custom_precision():
    class CustomPrecision(PLPrecisionPlugin):
        pass

    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"), pytest.raises(
        TypeError, match=escape("You passed an unsupported plugin as input to Lite(plugins=...)")
    ):
        EmptyLite(plugins=CustomPrecision())


@RunIf(deepspeed=True)
def test_lite_convert_pl_strategies_deepspeed():
    with pytest.deprecated_call(match="will be renamed to `lightning.fabric.Fabric` in v2.0.0"):
        lite = EmptyLite(strategy=PLDeepSpeedStrategy(stage=2, initial_scale_power=32, loss_scale_window=500))
    assert isinstance(lite._strategy, LiteDeepSpeedStrategy)
    assert lite._strategy.config["zero_optimization"]["stage"] == 2
    assert lite._strategy.initial_scale_power == 32
    assert lite._strategy.loss_scale_window == 500
