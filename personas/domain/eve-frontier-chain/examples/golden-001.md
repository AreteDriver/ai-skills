# Eve Frontier Chain Response
## Example Output
```
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.24;

import { System } from "@latticexyz/world/src/System.sol";
import { WatcherTable } from "../codegen/tables/WatcherTable.sol";

contract WatcherSystem is System {
    /// @notice Record a reputation score on-chain
    /// @param entityId The smart character entity ID
    /// @param score Composite reputation score (0-1000)
    /// @param dimensions Packed dimension scores
    function recordReputation(
        uint256 entityId,
        uint256 score,
        bytes memory dimensions
    ) public {
        // Verify caller is authorized watcher
        address caller = _msgSender();
        require(isAuthorizedWatcher(caller), "Not authorized");

        WatcherTable.set(
            entityId,
            score,
            dimensions
```
