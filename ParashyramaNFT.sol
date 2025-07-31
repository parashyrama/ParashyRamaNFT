// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "contracts/token/ERC721/ERC721.sol";
import "contracts/access/Ownable.sol";
import "contracts/utils/Strings.sol";

contract ParashyramaNFT is ERC721, Ownable {
    using Strings for uint256;

    event TokenMinted(uint256 indexed tokenId, string name, string text);

    uint256 public tokenCounter;
    mapping(uint256 => string) private _tokenTexts;
    mapping(uint256 => string) private _tokenNames;

    uint256 public constant ROYALTY_PERCENTAGE = 10;

    constructor() ERC721("Parashyrama NFT", "PNFT") {
        tokenCounter = 0;
    }

    function mintTextNFT(string memory _name, string memory _text) public returns (uint256) {
        tokenCounter++;
        uint256 newTokenId = tokenCounter;

        _safeMint(msg.sender, newTokenId);
        _tokenTexts[newTokenId] = _text;
        _tokenNames[newTokenId] = _name;

        emit TokenMinted(newTokenId, _name, _text);
        return newTokenId;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "URI query for nonexistent token");

        string memory text = _tokenTexts[tokenId];
        string memory name = _tokenNames[tokenId];

        string memory svg = string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">',
                '<style>.title { font: bold 24px serif; fill: black; }</style>',
                '<rect width="100%" height="100%" fill="white"/>',
                '<text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" class="title">',
                    name,
                '</text>',
            '</svg>'
        ));

        string memory escaped_svg = _replace(svg, '"', '\\"');
        string memory image = string(abi.encodePacked("data:image/svg+xml;utf8,", escaped_svg));

        string memory json = string(abi.encodePacked(
            '{',
                '"name": "', name, '",',
                '"description": "', text, '",',
                '"image": "', image, '",',
                '"attributes": [',
                    '{ "trait_type": "Type", "value": "Poetry" },',
                    '{ "trait_type": "Storage", "value": "Fully On-Chain" },',
                    '{ "trait_type": "Royalty", "value": "', uint256(ROYALTY_PERCENTAGE).toString(), '%" }',
                ']',
            '}'
        ));

        return string(abi.encodePacked("data:application/json;utf8,", json));
    }

    function _replace(string memory input, string memory target, string memory replacement) internal pure returns (string memory) {
        bytes memory inputBytes = bytes(input);
        bytes memory targetBytes = bytes(target);
        bytes memory replacementBytes = bytes(replacement);

        uint256 targetLength = targetBytes.length;
        uint256 replacementLength = replacementBytes.length;
        uint256 inputLength = inputBytes.length;

        uint256 occurrences = 0;
        for (uint256 i = 0; i <= inputLength - targetLength; i++) {
            bool matchFound = true;
            for (uint256 j = 0; j < targetLength; j++) {
                if (inputBytes[i + j] != targetBytes[j]) {
                    matchFound = false;
                    break;
                }
            }
            if (matchFound) {
                occurrences++;
            }
        }

        bytes memory newBytes = new bytes(inputLength + occurrences * (replacementLength - targetLength));
        uint256 k = 0;
        for (uint256 i = 0; i < inputLength; i++) {
            if (i <= inputLength - targetLength && _matchSubstring(inputBytes, i, targetBytes)) {
                for (uint256 j = 0; j < replacementLength; j++) {
                    newBytes[k++] = replacementBytes[j];
                }
                i += targetLength - 1;
            } else {
                newBytes[k++] = inputBytes[i];
            }
        }

        return string(newBytes);
    }

    function _matchSubstring(bytes memory inputBytes, uint256 index, bytes memory targetBytes) internal pure returns (bool) {
        for (uint256 i = 0; i < targetBytes.length; i++) {
            if (inputBytes[index + i] != targetBytes[i]) {
                return false;
            }
        }
        return true;
    }
}
