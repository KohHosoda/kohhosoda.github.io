//
// Kalman Filterのテスト，モータのケース
//
clf();

T=0.001;                    // 周期
Tf=3;                 // 終了時間
t=0:T:Tf;
N=length(t);
// システムノイズ
vv=rand(t,"normal");
sv=0.01;                  // システムノイズ σv
v=sv*vv;

// システムのダイナミクス
A=[0 1; -36 -3.6];
B=[0;36];
c=[1;0];
AA=[1 0;0 1]+A*T;
BB=B*T;
// システムの時間発展
x0=[0.5;0];            // システムの初期値
x1=x0;                    // 真の状態x1 の初期化
for i=1:N-1
    x1(:,i+1)=AA*x1(:,i)+BB*v(i);
end
// 真の値のプロット(red)
subplot(2,1,1);
xtitle("モータの角度","t");
//a=gca(); //アクティブな軸のオブジェクトを取得
//a.data_bounds(:,2)=[-2;1]; //Y軸の範囲
plot(t,x1(1,:),"color","red");
subplot(2,1,2);
xtitle("モータの角速度","t");
plot(t,x1(2,:),"color","red");

// 差分で速度を推定する
Ts=0.01;            // サンプリング時間
tt=0:Ts:Tf;
N=length(tt);
// 観測ノイズ
ww=rand(tt,"normal");
sw=0.01                  // 観測ノイズ σw
w=sw*ww;
for i=1:N
    y(i)=c'*x1(:,int(Ts*(i-1)/T)+1)+w(i);
end
// システムのモデル
AA=[1 0;0 1]+A*Ts;
BB=B*Ts;
// 推定値（領域確保）の初期化
xhat=zeros(2,N);
xhatb=zeros(2,N);
xhat(:,1)=[0 0];               // 推定値の初期化
xhatb(:,1)=[0 0];
gamma=0.1;
P=gamma*[1 0;0 1];
Pb=gamma*[1 0;0 1];
for k=2:N
    xhatb(:,k)=AA*xhat(:,k-1);
    Pb=AA*P*AA'+BB*BB'*sv*sv;
    g=(Pb*c)/(c'*Pb*c+sw*sw);
    xhat(:,k)=xhatb(:,k)+g*(y(k)-c'*xhatb(:,k));
    P=([1 0;0 1]-g*c')*Pb;
end
subplot(2,1,1);
//a=gca(); //アクティブな軸のオブジェクトを取得
//a.data_bounds(:,2)=[-2;1]; //Y軸の範囲
plot(tt,xhat(1,:),"color","blue");
subplot(2,1,2);
plot(tt,xhat(2,:),"color","blue");


