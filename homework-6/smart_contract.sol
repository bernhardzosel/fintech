// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SharedGift {
    address payable[] public contributors;
    uint public giftValue;
    uint public totalContributed;
    bool public giftPurchased;

    constructor(uint _giftValue, address payable[] memory _contributors) {
        giftValue = _giftValue;
        contributors = _contributors;
        giftPurchased = false;
    }

    function contribute() public payable {
        require(!giftPurchased, "Gift already purchased.");
        require(msg.value > 0, "Contribution must be more than 0.");
        totalContributed += msg.value;
    }

    function purchaseGift(address payable vendor) public {
        require(totalContributed >= giftValue, "Insufficient funds collected.");
        require(!giftPurchased, "Gift already purchased.");
        require(isContributor(msg.sender), "Only contributors can purchase the gift.");

        vendor.transfer(address(this).balance);
        giftPurchased = true;
    }

    function isContributor(address _address) internal view returns(bool) {
        for (uint i = 0; i < contributors.length; i++) {
            if (contributors[i] == _address) {
                return true;
            }
        }
        return false;
    }
}
