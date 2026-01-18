const N = 300;
const W = 600;
const CELL = W / N;
const ctx = c.getContext("2d");
const img = ctx.createImageData(W, W);

let J = 1;
let T = 1;
let B = 0;
let paused = false;
let speed = 1;

const ws = new WebSocket("ws://localhost:8000/ws");

ws.binaryType = "arraybuffer";

ws.onmessage = e => {
  const data = new Int8Array(e.data);
  for (let x=0;x<N;x++)
    for (let y=0;y<N;y++) {
      const v = data[x*N+y] === 1 ? 255 : 0;
      for (let i=0;i<CELL;i++)
        for (let j=0;j<CELL;j++) {
          const p = 4*((y*CELL+j)*W+(x*CELL+i));
          img.data[p]=img.data[p+1]=img.data[p+2]=v;
          img.data[p+3]=255;
        }
    }
  ctx.putImageData(img,0,0);
};

function sendParams(){
    ws.send(JSON.stringify({
        type: "params",
        T: T,
        J: J,
        B: B,
        speed: speed,
        paused: paused,
    }));
}

document.getElementById("T").oninput = e => {
  T = parseFloat(e.target.value);
  if (T==0){
    T = 0.0000000001;
  }
  sendParams();
};

document.getElementById("J").oninput = e => {
  J = parseFloat(e.target.value);
  sendParams();
};

document.getElementById("B").oninput = e => {
  B = parseFloat(e.target.value);
  sendParams();
};

document.getElementById("speed").oninput = e => {
  speed = parseFloat(e.target.value);
  sendParams();
};

document.getElementById("pause").onclick = () => {
  paused = !paused;
  sendParams();
};