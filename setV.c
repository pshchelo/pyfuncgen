#include <visa.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <windows.h>

int sec=1000,t;
double f, u, dt=5;

void PrintDisp (ViSession vi, char * string)
{
    char text[100]="DISP:TEXT \'";
    strcat(text,string);
    strcat(text,"\'\n");
    viPrintf(vi,text);
}

void PrintDisp1 (ViSession vi, int nr, char * string)
{
    char text[200]="DISP:TEXT \'", tmp[255];
    
    strcpy(text,string);
    sprintf(tmp," %d:%2.2d\r%4.2f Hz | %4.2f Vp  ",(int)(t-nr)/60,(t-nr)%60,f,u);
    strcat(text,tmp);
    PrintDisp(vi,text);
    printf(tmp);
}

int main (int argc, char *argv[])
{
    ViSession defaultRM, vi;
    //char buf [256] = {0};
    char instr [10]="MY44011622",tot [25]= "USB0::2391::1031::";
    int i,t1,t2,t3;
    double u1,u2,a,b,f1,f2;
  
    if(argc>1)
        if(atoi(argv[1])== 2)
            strcpy(instr,"MY44020723");
    strcat(tot,instr);
    strcat(tot,"::0::INSTR");
    viOpenDefaultRM (&defaultRM);
    viOpen (defaultRM, tot, VI_NULL,VI_NULL, &vi);
    viPrintf (vi, "*RST\n");
    if (argc<9)
    {
            printf("args: device f1 u1 u2 t1 t2 f2 t3");
            return 0;
    }
    f1=(double)atof(argv[2]);
    u1=(double)atof(argv[3]);
    if(u1==0)
        u1=0.0001;
    u2=(double)atof(argv[4]);
    t1=(int)atoi(argv[5])*60;
    t2=(int)atoi(argv[6])*60;
    f2=(double)atof(argv[7]);
    t3=(int)atoi(argv[8])*60;

    // stage 1: increase u1 to u2 in time t1
    f=f1;t=t1;
    printf("Growing stage\n");
    PrintDisp(vi,"Starting!");
    a=(u2-u1)/(double)t1;
    u=a*1.+u1;
    viPrintf(vi,"APPL:SIN %f, %f\n",f1,u1);
    Sleep(dt*200);
    for(i=dt;i<=t1;i+=dt)
    {
            u=a*i+u1;
            PrintDisp1(vi,i,"Growing");
            viPrintf(vi,"volt %f\n",u);
            Sleep(dt*sec);
    }

    // stage 2: const u2 for t2 (sleeping time)
    t=t2;
    printf("\nResting stage\n");
    for(i=0;i<t2;i+=dt)
    {
            PrintDisp1(vi,i,"Resting");
            Sleep(dt*sec);      
    }       

    // stage 3: detaching
    printf("\nDetaching stage\n");
    a=(f2-f)/(double)(t3);
    b=f;t=t3;
    for(i=0;i<=t3;i+=dt)
    {
        f=a*(double)(i)+b;
        PrintDisp1(vi,i,"Detaching");
        viPrintf(vi,"FREQ %f\n",f);
        Sleep(dt*sec);
    }
    i=0;t=0;
    printf("\nFINISHED!\nHit key to finish\n");
    while(!kbhit())
    {  
        PrintDisp1(vi,i-=dt,"FINISHED!");
        Sleep(dt*sec);  
    } 
      PrintDisp(vi,"Finished!");
      viClose (vi);
      viClose (defaultRM);
      return 0;
}
