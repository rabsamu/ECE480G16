void runFilter(float args[16]) {
  float runTime = args[1];

  setFilter(75);
  delay(runTime*1000);
  setFilter(0);
}
