// 废

function  typeis(any, type): boolean {
    return typeof(any)==type;
}

function waitutil(condition: boolean) {
    while(condition);
}

async function readFile(address: String) {
    if(!typeis(address, String)) {
        throw TypeError("Arg 'address' must be String, not'%s'.".replace('%s', typeof(address).toString()));
    }
    try {
        const fs = require('fs').promises;
        const path = require('path');
        return await fs.readFile(path.join(path.dirname(address), address), 'utf8');
    } catch (err) {
        console.error('data读取失败: ', err.message);
        return NaN;
    }
}