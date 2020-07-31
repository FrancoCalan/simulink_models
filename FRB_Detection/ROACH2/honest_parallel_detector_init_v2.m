

function honest_parallel_detector_init_v2(blk,varargin)

if same_state(blk,varargin(:)), return, end % if it has the same state that already has, just get out

% disable link to the library so you can edit freely this block when you
% use it in a model:
munge_block(blk,varargin(:));

%Get parameters into variables
n_inputs = get_var('n_inputs',varargin{:}); % get variable from the varargin given to the function
DM_Vector = get_var('DM_Vector',varargin{:}); % pay attention to brackets
nbits = get_var('nbits',varargin{:});

%Examples (for debugging)
% n_inputs = 4;
% DM_Vector = [1:1:64];
% nbits = 2;

n_channels = length(DM_Vector); % Number of total channels from the FFT

channels_input = n_channels/n_inputs; % Number of channels per input

DM_Matrix = zeros(n_inputs,channels_input); % Matrix containing dedispersion vectors

% We take advantage of Matlab's native definition of matrix single-indexes
% Then we get a row adjusted vector for every stream of FFT
for i=1:n_channels
    DM_Matrix(i) = DM_Vector(i);
end

%Erase every line in block
delete_lines(blk);

% Initialize blocks (by reusing them from library)

%Inputs
in_x = 30; % x block dimension
in_y = 14; % y block dimension 
reuse_block(blk,'Valid','built-in/inport','Port','1','Position',get_position(0,0,in_x,in_y)); 
for i=1:n_inputs
    port_num = num2str(1+i);
    port_name = strcat('Data',num2str(i));
    reuse_block(blk,port_name,'built-in/inport','Port',port_num,'Position',get_position(0,200+200*(i-1),in_x,in_y));
end

%Dedispersor Blocks
d_x = 115;
d_y = 112;
for i=1:n_inputs
    dd_name = strcat('Dedispersor_v2_',num2str(i));
    reuse_block(blk,dd_name,'HonestLibrary/Dedispersor_v2','DM_Vector',mat2str(DM_Matrix(i,:)),'nbits',num2str(nbits),'Position',get_position(200,200*i,d_x,d_y));
end

%Outputs
o_x = 30;
o_y = 14;
for i=1:n_inputs
    port_num = num2str(i);
    port_name = strcat('Out',num2str(i));
    reuse_block(blk,port_name,'built-in/outport','Port',port_num,'Position',get_position(400,250+200*(i-1),o_x,o_y));
end


%Connect Blocks

%Valid input to Dedispersor blocks
for i=1:n_inputs
   dd_name = strcat('Dedispersor_v2_',num2str(i),'/2');
   add_line(blk,'Valid/1',dd_name,'autorouting','on');
end

%Input ports to Dedispersor blocks
for i=1:n_inputs
    in_name = strcat('Data',num2str(i),'/1');
    dd_name = strcat('Dedispersor_v2_',num2str(i),'/1');
    add_line(blk,in_name,dd_name,'autorouting','on');
end

%Output ports to Dedispersor blocks
for i=1:n_inputs
    dd_name = strcat('Dedispersor_v2_',num2str(i),'/1');
    out_name = strcat('Out',num2str(i),'/1');
    add_line(blk,dd_name,out_name,'autorouting','on');
end


%Final Setup

% use this to show on model the parameters of your block
set_param(blk, 'AttributesFormatString',['Inputs: ',num2str(n_inputs),', Channels: ',num2str(n_channels)])

% Finds any block that it's not wired and removes it
clean_blocks(blk);

% Save state and parameters of block
save_state(blk,varargin{:});