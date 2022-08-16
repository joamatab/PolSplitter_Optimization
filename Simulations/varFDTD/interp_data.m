file = fopen('2D_parameters.txt','r')
data = fscanf(file,'%f')
fclose(file)
data_top = data(1:length(data)/2)
data_bot = data(length(data)/2+1:end)
y0 = 0.0e-6
wg01 = 0.5e-6
n_wg01 = 0.5e-6

%% 
x = linspace(-2.5,2.5,21);
new_x = linspace(-2.5,2.5,11);
n_y0 = 0.0e-6;
dy = y0 - n_y0;



new_data_top = interp1(x,data_top,new_x,"cubic")+dy;
new_data_bot = interp1(x,data_bot,new_x,"cubic")-dy;

plot(x,y0+data_top), hold on, 
plot(x,y0-data_bot), 

plot(new_x,n_y0+new_data_top,'x'),  hold on
plot(new_x,n_y0-new_data_bot,'x')
legend
hold off

new_data = [new_data_top'; new_data_bot']

%% Check generated Structure
%figure(1)
points_x1 = [min(new_x)-0.05,new_x,max(new_x)+0.05];

y1 = n_y0 + n_wg01 / 2;
y2 = (0.35e-6/2+0.5e-6);
points_y1 = [y1,n_y0+new_data_top,y2]

y1 = n_y0 - n_wg01 / 2;
y2 = -(0.35e-6/2+0.5e-6);
points_y2 = [y1,n_y0-new_data_bot,y2]

xx = linspace(min(points_x1),max(points_x1),101);
yy_top = interp1(points_x1,points_y1,xx,"cubic");
yy_bot = interp1(points_x1,points_y2,xx,"cubic");

hold on
plot(xx,yy_top), hold on, 
plot(xx,yy_bot), hold off
