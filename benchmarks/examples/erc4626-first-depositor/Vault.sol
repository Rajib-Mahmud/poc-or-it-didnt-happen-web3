// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/// @title  SimpleVault
/// @notice A minimal ERC-4626-style vault: deposit the underlying asset to receive shares,
///         redeem shares to withdraw the underlying. Assumes a standard ERC-20 asset.
contract Vault {
    IERC20 public immutable asset;
    address public owner;
    address public feeRecipient;

    uint256 public totalSupply;                 // total shares
    mapping(address => uint256) public balanceOf;

    event Deposit(address indexed caller, uint256 assets, uint256 shares);
    event Withdraw(address indexed caller, uint256 assets, uint256 shares);

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(IERC20 _asset) {
        asset = _asset;
        owner = msg.sender;
        feeRecipient = msg.sender;
    }

    /// @notice Total underlying assets managed by the vault.
    function totalAssets() public view returns (uint256) {
        return asset.balanceOf(address(this));
    }

    /// @notice Shares minted for a given deposit of assets.
    function previewDeposit(uint256 assets) public view returns (uint256) {
        uint256 supply = totalSupply;
        if (supply == 0) {
            return assets;
        }
        return (assets * supply) / totalAssets();
    }

    /// @notice Assets returned for a given redemption of shares.
    function previewRedeem(uint256 shares) public view returns (uint256) {
        uint256 supply = totalSupply;
        if (supply == 0) return 0;
        return (shares * totalAssets()) / supply;
    }

    /// @notice Deposit `assets` of the underlying and receive shares.
    function deposit(uint256 assets) external returns (uint256 shares) {
        shares = previewDeposit(assets);
        asset.transferFrom(msg.sender, address(this), assets);
        totalSupply += shares;
        balanceOf[msg.sender] += shares;
        emit Deposit(msg.sender, assets, shares);
    }

    /// @notice Redeem `shares` and receive the underlying assets.
    function redeem(uint256 shares) external returns (uint256 assets) {
        require(balanceOf[msg.sender] >= shares, "insufficient shares");
        assets = previewRedeem(shares);
        balanceOf[msg.sender] -= shares;
        totalSupply -= shares;
        asset.transfer(msg.sender, assets);
        emit Withdraw(msg.sender, assets, shares);
    }

    /// @notice Update the protocol fee recipient.
    function setFeeRecipient(address _feeRecipient) external onlyOwner {
        feeRecipient = _feeRecipient;
    }
}
