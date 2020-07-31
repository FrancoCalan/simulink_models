


function honest_detector_v2(DM_Vector,nbits)

%DM_Vector = [0:1:15]                        %Example DM Vector (for debugging)
%nbits = 8                                   %Example nbits (for debugging)

n_channels = length(DM_Vector);             % Number of channels and basic blocks

[a,b] = xInport('Data','Valid');            % In ports of subsystem
out = xOutport('Output');                   % Out ports of subsystem


%Create names for detector blocks
det_name = {};
for i = 1:n_channels
    det_name{end+1} = strcat('detector',num2str(i));  %det_name{end+1} = 'detector<number>'
end 

% Create n_channels signals to connect at detector blocks outputs with
% multiplexer block
mux_signals = {};
for i = 1:n_channels
    mux_signals{end+1} = xSignal;
end

% Create n_channels detector blocks with names det_names, using xBlock.
% Each detector block it's connected to a 'mux signal' output.
for i = 1:n_channels
    det_name(i) = xBlock('honestlibrary/detector_block_v2',struct('chn',i-1,'lat',DM_Vector(i)+1,'nbits',nbits),{a,b},{mux_signals{i}});
end

% Separate cases:
% 1.- Single multiplexer
% 2.- Two stage multiplexer
% This comes from the fact that Xilinx's mux max number of inputs it's 32



% Case 1: Single mux
if n_channels <= 32
    
    mux_out = xSignal;              % Output signal of multiplexer 
    mux_input = [{b},mux_signals];  % Add 'sel' signal to the first element of mux inputs
    mux1 = xBlock('Mux',struct('inputs',n_channels),mux_input,{mux_out});   % Create Multiplexer with #(n_channels) inputs
    out.bind(mux_out);                                                      % Bind mux_out with out port of subsystem
end



% Case 2: Two stage multiplexation
if (n_channels <= 1024) && (n_channels > 32)
    number_muxes = ceil(n_channels/32);         % Number of muxes to create equal to the number of inputs of selector mux
    bits_selector = ceil(log2(n_channels))-5;   % Number of bits required from the counter signal to the selector mux from MSB to LSB
    
    common_mux = xSignal;   % Signal to common muxs
    stage_mux = xSignal;    % Signal to stage mux which selects a single mux for output
    
    slice_common = xBlock('Slice',struct('nbits',5,'mode','Lower Bit Location + Width'),{b},{common_mux});               % Select bits of 'Count' common muxes
    slice_stage = xBlock('Slice',struct('nbits',bits_selector,'mode','Upper Bit Location + Width'),{b},{stage_mux});     % Select bits of 'Count' stage mux
    
    % Create number_muxes signals for muxes' outputs and names/tags
    mux_out = {};
    mux_name = {};
    for i = 1:number_muxes
        mux_out{end+1} = xSignal;
        mux_name{end+1} = strcat('Multiplexer',num2str(i));
    end

    % Create muxes of first stage
    for i = 1:number_muxes
        mux_name(i) = xBlock('Mux' , struct('inputs','32') ,  [{common_mux}, mux_signals(1+32*(i-1) : 32+32*(i-1))] , mux_out(i) );
    end
    
    % Create mux of second stage
    
    mux_stage = xBlock('Mux', struct('inputs',number_muxes),[{stage_mux},mux_out],{out});
 
    
    
end
