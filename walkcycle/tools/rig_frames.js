/*
 * 원본 페이지의 character.js(걷기 리그)로 걷기 8프레임과 정지 포즈를 128x128 RGBA 원시 파일로 뽑는다.
 * 포즈 가이드(make_pose_guide.py)와 비교 이미지(make_preview.py)의 입력이 된다.
 *
 *   node rig_frames.js <character.js 경로> <out_dir>
 *
 * character.js 는 이 저장소에 들어 있지 않다. 원본 페이지에서 받아 경로를 넘긴다.
 */
const path = require('path'), fs = require('fs');
const Ch = require(path.resolve(process.argv[2]));
const out = process.argv[3];
fs.mkdirSync(out, { recursive: true });

function dump(name, pose, scarf) {
  const cell = new Uint32Array(Ch.W * Ch.H);
  Ch.render(cell, pose, scarf);
  fs.writeFileSync(path.join(out, name + '.rgba'), Buffer.from(cell.buffer));
}

Ch.walkFrames(8).forEach((f, i) => dump('walk' + i, f.pose, f.scarf));

// 정지 포즈: 스카프가 가라앉을 때까지 물리를 돌린 뒤 찍는다
const sim = new Ch.ScarfSim();
const p = Ch.pose(0, 0, 0);
for (let k = 0; k < 600; k++) sim.step(1 / 120, p.scarfAnchor[0], p.scarfAnchor[1], 0, 16, 0);
dump('idle', p, sim.local(0, 1));

console.log('frames written to', out, '| stride', Ch.STRIDE.toFixed(2), 'px/cycle, cadence', Ch.CADENCE, 'cycles/s');
