import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow.python import tf2
from normalizing_flows import FLOWS
from normalizing_flows import AffineFlow
import pytest

if not tf2.enabled():
    import tensorflow.compat.v2 as tf

    tf.enable_v2_behavior()
    assert tf2.enabled()
tfd = tfp.distributions


def flow_dimension_testing(flow_name):
    # all are tested again Affine Flow, since that's the reference implementation
    batch_size = 10
    for dim in [1, 4]:
        flow_class = FLOWS[flow_name]
        # test dimension of parameter space
        with pytest.raises(AssertionError):
            flow = flow_class(
                tf.ones((batch_size, flow_class.get_param_size(dim) + 1)), dim
            )

        flow = flow_class(tf.ones((batch_size, flow_class.get_param_size(dim))), dim)
        reference = AffineFlow(
            tf.ones((batch_size, AffineFlow.get_param_size(dim))), dim
        )

        test_tensors = [[[0.0] * dim], [[1.0] * dim] * batch_size]
        assert flow.forward_min_event_ndims == reference.forward_min_event_ndims
        for tensor in test_tensors:
            assert flow.inverse(tensor).shape == reference.inverse(tensor).shape
            assert (
                flow._inverse_log_det_jacobian(tensor).shape
                == reference._forward_log_det_jacobian(tensor).shape
            )

        tensor = [[1.0] * dim] + ([[0.0] * dim] * (batch_size - 2)) + [[1.0] * dim]
        res = flow.inverse(tensor).numpy()
        assert all(res[0] == res[-1])
        assert all(res[1] == res[-2])
        assert not all(res[0] == res[1])

        tensor = [[1.0] * dim] + ([[0.0] * dim] * (batch_size - 2)) + [[1.0] * dim]
        res = flow._inverse_log_det_jacobian(tensor).numpy()
        assert res[0] == pytest.approx(res[-1])
        assert res[1] == pytest.approx(res[-2])
        assert not res[0] == pytest.approx(res[1])


def test_planar():
    flow_dimension_testing("planar")


def test_radial():
    flow_dimension_testing("radial")
