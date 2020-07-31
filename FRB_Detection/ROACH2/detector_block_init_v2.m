

function detector_block_init_v2(blk,varargin)

if same_state(blk,varargin(:)), return, end %if it has the same state that already has get out

% disable link to the library so you can edit freely this block when you
% use it in a model:
munge_block(blk,varargin(:));

%Get parameters into variables
chn = get_var('chn',varargin{:}); % get variable from the varargin given to the function
lat = get_var('lat',varargin{:}); % pay attention to brackets
nbits = get_var('nbits',varargin{:});

%Erase every line in block
delete_lines(blk);

% Initialize blocks (by reusing them from library)

%Inputs
in_x = 30; % x block dimension
in_y = 14; % y block dimension 
reuse_block(blk,'Data','built-in/inport','Port','1','Position',get_position(100,100,in_x,in_y));
reuse_block(blk,'Valid','built-in/inport','Port','2','Position',get_position(100,200,in_x,in_y)); 

%Constants
c_x = 30; % x block dimension
c_y = 26; % y block dimension
reuse_block(blk,'Const1','xbsIndex_r4/Constant','const',num2str(chn),'n_bits','16','bin_pt','0','Position',get_position(200,300,c_x,c_y));

%Counter
cnt_x = 50;
cnt_y = 56;
reuse_block(blk,'Counter1','xbsIndex_r4/Counter','n_bits',num2str(nbits),'Position',get_position(200,200,cnt_x,cnt_y));

%Relational
r_x = 50;
r_y = 56;
reuse_block(blk,'Relational1','xbsIndex_r4/Relational','latency','0','Position',get_position(300,200,r_x,r_y));

%Expression
e_x = 50;
e_y = 56;
reuse_block(blk,'Expression1','xbsIndex_r4/Expression','expression','a & b','Position',get_position(400,250,e_x,e_y));

%Delay
d_x = 60;
d_y = 56;
reuse_block(blk,'Delay1','xbsIndex_r4/Delay','latency',num2str(lat),'Position',get_position(500,200,d_x,d_y));

%Output
o_x = 30;
o_y = 14;
reuse_block(blk,'Out1','built-in/outport','Port','1','Position',get_position(600,200,in_x,in_y)); 

% Connect Blocks

%Counter Inputs
add_line(blk,'Valid/1','Counter1/1','autorouting','on')

%Relational Inputs
add_line(blk,'Counter1/1','Relational1/1','autorouting','on')
add_line(blk,'Const1/1','Relational1/2','autorouting','on')

%Expression Inputs
add_line(blk,'Relational1/1','Expression1/1','autorouting','on')
add_line(blk,'Valid/1','Expression1/2','autorouting','on')

%Delay Inputs
add_line(blk,'Data/1','Delay1/1','autorouting','on')
add_line(blk,'Expression1/1','Delay1/2','autorouting','on')

%Output Inputs
add_line(blk,'Delay1/1','Out1/1','autorouting','on')

%Final Setup

% use this to show on model the parameters of your block
set_param(blk, 'AttributesFormatString',['Channel: ',num2str(chn),', Delay: ',num2str(lat)])

% Finds any block that it's not wired and removes it
clean_blocks(blk);

% Save state and parameters of block
save_state(blk,varargin{:});

end
