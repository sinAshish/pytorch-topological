"""Check optimal transport integration."""


import numpy as np

import ot
import torch

from ot.datasets import make_1D_gauss as gauss


class WassersteinDistanceLoss(torch.nn.Module):
    # TODO: q is still unused
    def __init__(self, p=torch.inf, q=1):
        super().__init__()

        self.p = p
        self.q = q

    def _project_to_diagonal(self, diagram):
        x = diagram[:, 0]
        y = diagram[:, 1]

        # TODO: Is this the closest point in all p-norms?
        return 0.5 * torch.stack(((x + y), (x + y)), 1)

    def _distance_to_diagonal(self, diagram):
        return torch.linalg.vector_norm(
            diagram - self._project_to_diagonal(diagram),
            self.p,
            dim=1
        )

    def _make_distance_matrix(self, D1, D2):
        dist_D11 = self._distance_to_diagonal(D1)
        dist_D22 = self._distance_to_diagonal(D2)

        # n x m matrix containing the distances between 'regular'
        # persistence pairs of both persistence diagrams.
        dist = torch.cdist(D1, D2, p=torch.inf)

        # Extend the matrix with a column of distances of samples in D1
        # to their respective projection on the diagonal.
        upper_blocks = torch.hstack((dist, dist_D11[:, None]))

        # Create a lower row of distances of samples in D2 to their
        # respective projection on the diagonal. The ordering needs
        # to follow the ordering of samples in D2. Note how one `0`
        # needs to be added to the row in order to balance it. The
        # entry intuitively describes the cost between *projected*
        # points, so it has to be zero.
        lower_blocks = torch.cat((dist_D22, torch.tensor(0).unsqueeze(0)))

        # Full (n + 1 ) x (m + 1) matrix containing *all* distances. By
        # construction, M[[i, n] contains distances to projected points
        # in D1, whereas M[m, j] does the same for points in D2. Only a
        # cell M[i, j] with 0 <= i < n and 0 <= j < m contains a proper
        # distance.
        M = torch.vstack((upper_blocks, lower_blocks))

        return M


    def forward(self, D1, D2):
        n = len(D1)
        m = len(D2)

        dist = self._make_distance_matrix(D1, D2)

        # Create weight vectors. Since the last entries of entries
        # describe the m points coming from D2, we have to set the
        # last entry accordingly.

        a = torch.ones(n + 1)
        b = torch.ones(m + 1)

        a[-1] = m
        b[-1] = n

        # TODO: Make settings configurable?
        return ot.emd2(a, b, dist)


PD1 = [
    (0, 0),
    (1, 2),
    (3, 4)
]

PD2 = [
    (0, 0),
    (3, 4),
    (5, 3),
    (7, 4)
]


PD1 = torch.as_tensor(PD1, dtype=torch.float)
PD2 = torch.as_tensor(PD2, dtype=torch.float)
print(PD1)
print(PD2)
print(WassersteinDistanceLoss()._make_distance_matrix(PD1, PD2))
print(WassersteinDistanceLoss()(PD1, PD2))