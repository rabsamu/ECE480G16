void runFilter(float args[16]) {
  float filterTime = args[1];
  float solutionTime = args[2];
  float bufferTime = args[3];

  setFilter(75);
  if(waitSeconds(filterTime)) return;
  setFilter(0);

  setSolution(75);
  waitSeconds(solutionTime);
  setSolution(0);

  setBuffer(75);
  waitSeconds(bufferTime);
  setBuffer(0);
}
