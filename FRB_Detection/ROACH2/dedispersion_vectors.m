

function DM_matrix = dedispersion_vectors(n_inputs,DM_vector)

n_channels = length(DM_vector); % Number of total channels from the FFT

channels_input = n_channels/n_inputs; % Number of channels per input of total DM

DM_matrix = zeros(n_inputs,channels_input); % Matrix containing dedispersion vectors

% We take advantage of Matlab's native definition of matrix single-indexes
for i=1:n_channels
    DM_matrix(i) = DM_vector(i);
end


