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

    uint256 private constant VIRTUAL = 1e6;     // virtual shares/assets for price stability

    uint256 public totalSupply;                 // total shares
    mapping(address => uint256) public balanceOf;

    uint256 private _locked = 1;

    event Deposit(address indexed caller, uint256 assets, uint256 shares);
    event Withdraw(address indexed caller, uint256 assets, uint256 shares);

    modifier nonReentrant() {
        require(_locked == 1, "reentrancy");
        _locked = 2;
        _;
        _locked = 1;
    }

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
        return (assets * (totalSupply + VIRTUAL)) / (totalAssets() + 1);
    }

    /// @notice Assets returned for a given redemption of shares.
    function previewRedeem(uint256 shares) public view returns (uint256) {
        uint256 denom = totalSupply + VIRTUAL;
        return (shares * (totalAssets() + 1) + denom - 1) / denom;
    }

    /// @notice Deposit `assets` of the underlying and receive shares.
    function deposit(uint256 assets) external nonReentrant returns (uint256 shares) {
        shares = previewDeposit(assets);
        require(shares > 0, "zero shares");
        asset.transferFrom(msg.sender, address(this), assets);
        totalSupply += shares;
        balanceOf[msg.sender] += shares;
        emit Deposit(msg.sender, assets, shares);
    }

    /// @notice Redeem `shares` and receive the underlying assets.
    function redeem(uint256 shares) external nonReentrant returns (uint256 assets) {
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
