import test from 'node:test';
import assert from 'node:assert/strict';
import { retryAfterMs } from './retry-after.mjs';

const cases = [
  ['2', 2000],
  ['0', 0],
  [' 2 ', 2000],
  ['0002', 2000],
  ['', null],
  ['   ', null],
  [undefined, null],
  [null, null],
  [2, null],
  ['0x10', null],
  ['2x', null],
  ['-1', null],
  ['1.5', null],
  ['1e3', null],
  ['Infinity', null],
  ['Wed, 21 Oct 2015 07:28:00 GMT', null],
  ['9007199254740', 9007199254740000],
  ['9007199254741', null],
  ['9007199254740991', null],
];
for (const [input, expected] of cases) {
  test(`retryAfterMs(${JSON.stringify(input)})`, () => {
    assert.equal(retryAfterMs(input), expected);
  });
}
