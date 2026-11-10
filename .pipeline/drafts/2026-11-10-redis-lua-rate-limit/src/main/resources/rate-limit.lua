local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
if not limit or limit < 1 or limit > 1000000 or limit ~= math.floor(limit)
   or not window or window < 1 or window > 3600000 or window ~= math.floor(window) then
    return redis.error_reply('invalid rate limit policy')
end

local raw = redis.call('GET', KEYS[1])
if raw then
    local count = tonumber(raw)
    local ttl = redis.call('PTTL', KEYS[1])
    if not count or count < 1 or count ~= math.floor(count) or ttl < 0 then
        return redis.error_reply('invalid counter state')
    end
    if count >= limit then
        return {0, 0, ttl}
    end
    local updated = redis.call('INCR', KEYS[1])
    return {1, limit - updated, ttl}
end

redis.call('SET', KEYS[1], 1, 'PX', window)
return {1, limit - 1, window}
