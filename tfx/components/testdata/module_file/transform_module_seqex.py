# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Python source file include taxi pipeline functions and necesasry utils.

For a TFX pipeline to successfully run, a preprocessing_fn and a
_build_estimator function needs to be provided.  This file contains both.

This file is equivalent to examples/chicago_taxi/trainer/model.py and
examples/chicago_taxi/preprocess.py.
"""

import tensorflow as tf
import tensorflow_transform as tft

# Number of buckets used by tf.transform for encoding each feature.
_FEATURE_BUCKET_COUNT = 10

# Number of vocabulary terms used for encoding VOCAB_FEATURES by tf.transform
_VOCAB_SIZE = 1000

# Count of out-of-vocab buckets in which unrecognized VOCAB_FEATURES are hashed.
_OOV_SIZE = 10


def _transformed_name(key):
  return key + '_xf'


def _fill_in_missing(x):
  """Replace missing values in a SparseTensor.

  Fills in missing values of `x` with '' or 0, and converts to a dense tensor.

  Args:
    x: A `SparseTensor` of rank 2.  Its dense shape should have size at most 1
      in the second dimension.

  Returns:
    A rank 1 tensor where missing values of `x` have been filled in.
  """
  if not isinstance(x, tf.sparse.SparseTensor):
    return x

  default_value = '' if x.dtype == tf.string else 0
  return tf.squeeze(
      tf.sparse.to_dense(
          tf.SparseTensor(x.indices, x.values, [x.dense_shape[0], 1]),
          default_value),
      axis=1)


@tf.function
def _identity(x):
  """Make sure everything still works when there is a tf.function used."""
  return x


def preprocessing_fn(inputs, custom_config):
  """tf.transform's callback function for preprocessing inputs.

  Args:
    inputs: map from feature keys to raw not-yet-transformed features.
    custom_config: additional properties for pre-processing.

  Returns:
    Map from string feature key to transformed features.
  """
  del custom_config  # Unused
  outputs = {}
  for key in ['f', 'i']:
    # If sparse make it dense, setting nan's to 0 or '', and apply zscore.
    outputs[_transformed_name(key)] = tft.scale_to_z_score(
        _fill_in_missing(_identity(inputs[key])))

  return outputs


def stats_options_updater_fn(unused_stats_type, stats_options):
  """Callback function for setting pre and post-transform stats options.

  Args:
    unused_stats_type: a stats_options_util.StatsType object.
    stats_options: a tfdv.StatsOptions object.

  Returns:
    An updated tfdv.StatsOptions object.
  """
  return stats_options
